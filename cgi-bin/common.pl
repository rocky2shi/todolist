
use Time::Local;




# ����Ŀ¼
$DATA_DIR = '../data';
$CR = "\1";

($g_sec,$g_min,$g_hour,$g_mday,$g_mon,$g_year,$g_wday,$g_yday,$g_isdst)=localtime(); #ʱ�����
$g_mon++;#��Ϊ�´�0��ʼ�����Ǵ�1990�����������������Ҫ����
$g_year += 1900;
$g_sec 	= "0$g_sec" if($g_sec < 10);
$g_min 	= "0$g_min" if($g_min < 10);
$g_hour = "0$g_hour" if($g_hour < 10);
$g_mday = "0$g_mday" if($g_mday < 10);
$g_mon 	= "0$g_mon" if($g_mon < 10);
$KEYSTRING = "$g_year$g_mon$g_mday$g_hour$g_min$g_sec";

##############################################################################

# ����
sub Debug
{
    my (undef, $file, $line) = caller();
    $file =~ s/.*\///;  # ȥ��·��
    open(DEBUG, ">>$ENV{DOCUMENT_ROOT}/../log/debug.txt") || return;
    print DEBUG  &TimeTo($KEYSTRING, 2) . " $file:$line>>> $_[0]\n";
    close(DEBUG);
}


sub cmpAB
{
	$a cmp $b;
}
sub cmpBA
{
	$b cmp $a;
}

#
# [Rocky 2009-07-29]
# ȡָ���ֽ����ݣ���������\r����\n��
# GetLine(FILE_ID, $size)
#
sub GetLine
{
    my ($file, $size) = @_;
    my ($buf, $c);

    for($i=0; $i<$size && read($file, $c, 1); $i++)
    {
        $buf .= $c;

        last if($c eq "\n");
    }

    return $buf;
}

#
# [Rocky 2009-07-29 23:41:07]
# �ֽ�GET��POST����
# ParseSubmit(\%in)
#
sub ParseSubmit
{
    my $in = $_[0];
    my $buf;
    my $tmp;
    my $boundary;
    my $id;
    my $filename;

    #
    # �ֽ��ļ��ϴ���POST����
    #
    if($ENV{'CONTENT_TYPE'} =~ /boundary=---------------------------[0-9]+$/)
    {
        binmode(STDIN) if($^O =~ /win/i);      # ��linux�ϲ���Ҫ�����ַ�ʽ���

        #
        # ȡboundary
        #
        $buf = GetLine(STDIN, 1024);
        if($buf !~ /(^-----------------------------[0-9]+)[\r|\n]$/)
        {
            return;
        }
        $boundary = $1;

        # DB("$boundary");

        srand(time());

        while( !eof(STDIN) )
        {
            $filename = "";
            $id = "";

            #
            # ȡͷ
            # Content-Disposition: form-data; name="import_zip1"; filename="a3.txt"
            #
            while( ($buf = GetLine(STDIN, 4096)) && ($buf !~ /^[\r\n]*$/) )
            {
                if($buf =~ / name=\"([^\"]*)\"; filename=\"([^\"]*)\"/s)
                {
                   $id = $1;
                   $filename = $2;
                }
                elsif($buf =~ / name=\"([^\"]*)\"/s)
                {
                    $id = $1;
                    $filename = "";
                }
                else
                {
                    next;
                }
                # DB("[$id] [$filename]");
            }

            #
            # ȡ��
            #
            if($filename ne "")
            {
                #
                # ���ļ�
                #
                $buf = GetLine(STDIN, 4096);
                if($buf eq "")
                {
                    return;
                }
                my $file = "$TMP/CGItemp." . rand() . ".tmp";
                open(POST_FILE, ">$file") or die "$!";
                binmode(POST_FILE);
                while( ($tmp = GetLine(STDIN, 4096))
                       && ($tmp !~ /^$boundary/) )
                {
                    print POST_FILE "$buf";
                    $buf = $tmp;
                }
                $buf =~ s/[\r\n]+$//;
                print POST_FILE "$buf";
                close(POST_FILE);
                # ��¼�ͻ����ļ���
                $in->{ $id } = $filename;
                # ���´��ļ����Ա��Ժ�ʹ�ã�
                open($in->{ $id }, "$file") or die "$!";
                binmode($in->{ $id });
            }
            else
            {
                #
                # �ǿؼ�����
                #
                while( ($buf = GetLine(STDIN, 4096))
                       && ($buf !~ /^$boundary/) )
                {
                    $in->{ $id } .= $buf;
                }
                $in->{ $id } =~ s/[\r\n]+$//;  # ɾȥ������ϵͳ�Զ����ϵĻس���
            }

            # �ҵ���boundary�� + ��--��˵����������
            if($buf =~ /^$boundary--[\r\n]*$/)
            {
                last
            }
        }
    }# end of if($ENV{'REQUEST_METHOD'} ...

    my ($post, $get);

    #
    # ����һ���POST����
    #
    if($ENV{'REQUEST_METHOD'} eq "POST")
    {
        read(STDIN, $post, $ENV{'CONTENT_LENGTH'});
    }

    #
    # ����һ���GET����
    #
    $get = $ENV{'QUERY_STRING'};

    #
    # ����
    #
    my $submit = $get . "&" . $post;
    my @in = split(/\&/, $submit);
    my ($k, $v, $i);
    foreach $i (@in)
    {
        next if($i eq "");
        ($k, $v) = split(/=/, $i);
        $v =~ s/\+/ /g;
        $k =~ s/%(..)/pack("c",hex($1))/ge;
        $v =~ s/%(..)/pack("c",hex($1))/ge;
        #$in->{$k} = defined($in->{$k}) ? $in->{$k}." ".$v : $v;
        #$in->{$k} = defined($in->{$k}) ? $in->{$k}."\0".$v : $v;
        $in->{$k} = $v;
    }

}

#����¼�ļ������ʽΪ.ini���磺
#
# [20060312184200]
# title=���Ǳ���
# text=��������
#
# read_file(file_name, array);
sub ReadFile
{
	local($/, $filename, $file, $key, @line);
	$filename = $_[0];
	
	open(FILE, $filename) || ($err="R002", return 0);
	$file = <FILE>;
	@line = split("\n", $file);
	close(FILE);
	
	$key='';
	foreach $buf (@line)
	{
		if($buf =~ /^\[(.*)\]/)
		{
			$key = $1;
		}
		next if($key eq '');
		
		if($buf =~ /(^[a-zA-Z\d\-_]+)=(.*)/)
		{
			$_[1]->{"$key"}{$1} = $2;
		}
	}
	return 1;
}

#��ReadFile���Ӧ
# $mode==2 : ׷�ӷ�ʽ
sub WriteFile
{
	local($filename, $item, $it, $file, $mode);
	$filename = $_[0];
	$mode = $_[2];
 	2==$mode?open(FILE, ">>$filename"):open(FILE, ">$filename") || ($err="W001", return 0);
 	$file = "#shizw\n";
	foreach $item (sort cmpAB keys %{$_[1]})#��һ��
	{
		$file .= "\n[$item]\n";
		foreach $it (sort cmpAB keys %{$_[1]->{$item}})#�ڶ���
		{
			$file .= "$it=$_[1]->{$item}{$it}\n";
		}
	}
	print FILE $file;	
	close(FILE);
	return 1;
}

#ʱ�䴮ת��
# 1. 20060324120254 => 2006��03��24��12��02��54��
# 2. 20060324120254 => 2006.03.24 12:02:54:
# TimeTo("20060324120254", 1)
sub TimeTo
{
	if(1==$_[1] && $_[0] =~ /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/)
	{
		return "$1��$2��$3��$4��$5��$6��";
	}
	if(2==$_[1] && $_[0] =~ /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/)
	{
		return "$1.$2.$3 $4:$5:$6";
	}
	if(3==$_[1] && $_[0] =~ /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/)
	{
		my @date = localtime(timelocal($6,$5,$4,$3,$2-1,$1));
		return "$1��$2��$3��$4��$5�� $WEEK[$date[6]]";
	}
	return $_[0];
}

#��Ǳ���
sub Escape
{
    local($tmp);
    $tmp = $_[0];
    #$tmp =~ s/&/&amp;/g;        # &    delete , 2009-08-23 22:10:08
    $tmp =~ s/</&lt;/g;         # <
    $tmp =~ s/>/&gt;/g;         # >
    #$tmp =~ s/\"/&quot;/g;      # "
    #$tmp =~ s/\'/&#39;/g;       # '
    #$tmp =~ s/=/&#61;/g;        # =
    return $tmp;
}

#ת���س����з�Ϊ�ڲ���ʾ��UnEnter�෴
sub Enter
{
    local($tmp);
    $tmp = $_[0];
    $tmp =~ s/\r//g;
    $tmp =~ s/\n/$CR/g;
    return $tmp;
}
sub UnEnter
{
    local($tmp);
    $tmp = $_[0];
    $tmp =~ s/$CR/\n/g;
    return $tmp;
}

# ת����url
# ChangeTo(url);
sub ChangeTo
{
	print "Location: $_[0]\n\n";
	exit(1);
}
