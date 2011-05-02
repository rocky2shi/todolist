
use Time::Local;




# 数据目录
$DATA_DIR = '../data';
$CR = "\1";

($g_sec,$g_min,$g_hour,$g_mday,$g_mon,$g_year,$g_wday,$g_yday,$g_isdst)=localtime(); #时间变量
$g_mon++;#因为月从0开始，年是从1990年算起的年数，所以要调整
$g_year += 1900;
$g_sec 	= "0$g_sec" if($g_sec < 10);
$g_min 	= "0$g_min" if($g_min < 10);
$g_hour = "0$g_hour" if($g_hour < 10);
$g_mday = "0$g_mday" if($g_mday < 10);
$g_mon 	= "0$g_mon" if($g_mon < 10);
$KEYSTRING = "$g_year$g_mon$g_mday$g_hour$g_min$g_sec";

##############################################################################

# 调试
sub Debug
{
    my (undef, $file, $line) = caller();
    $file =~ s/.*\///;  # 去掉路径
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
# 取指定字节数据，或遇到＂\r＂或＂\n＂
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
# 分解GET和POST请求
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
    # 分解文件上传的POST请求
    #
    if($ENV{'CONTENT_TYPE'} =~ /boundary=---------------------------[0-9]+$/)
    {
        binmode(STDIN) if($^O =~ /win/i);      # 在linux上不需要以这种方式输出

        #
        # 取boundary
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
            # 取头
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
            # 取体
            #
            if($filename ne "")
            {
                #
                # 是文件
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
                # 记录客户端文件名
                $in->{ $id } = $filename;
                # 重新打开文件，以便以后使用；
                open($in->{ $id }, "$file") or die "$!";
                binmode($in->{ $id });
            }
            else
            {
                #
                # 是控件数据
                #
                while( ($buf = GetLine(STDIN, 4096))
                       && ($buf !~ /^$boundary/) )
                {
                    $in->{ $id } .= $buf;
                }
                $in->{ $id } =~ s/[\r\n]+$//;  # 删去数据中系统自动加上的回车符
            }

            # 找到＂boundary＂ + ＂--＂说明到结束了
            if($buf =~ /^$boundary--[\r\n]*$/)
            {
                last
            }
        }
    }# end of if($ENV{'REQUEST_METHOD'} ...

    my ($post, $get);

    #
    # 处理一般的POST请求
    #
    if($ENV{'REQUEST_METHOD'} eq "POST")
    {
        read(STDIN, $post, $ENV{'CONTENT_LENGTH'});
    }

    #
    # 处理一般的GET请求
    #
    $get = $ENV{'QUERY_STRING'};

    #
    # 解析
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

#读记录文件，其格式为.ini，如：
#
# [20060312184200]
# title=这是标题
# text=这是内容
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

#和ReadFile相对应
# $mode==2 : 追加方式
sub WriteFile
{
	local($filename, $item, $it, $file, $mode);
	$filename = $_[0];
	$mode = $_[2];
 	2==$mode?open(FILE, ">>$filename"):open(FILE, ">$filename") || ($err="W001", return 0);
 	$file = "#shizw\n";
	foreach $item (sort cmpAB keys %{$_[1]})#第一层
	{
		$file .= "\n[$item]\n";
		foreach $it (sort cmpAB keys %{$_[1]->{$item}})#第二层
		{
			$file .= "$it=$_[1]->{$item}{$it}\n";
		}
	}
	print FILE $file;	
	close(FILE);
	return 1;
}

#时间串转换
# 1. 20060324120254 => 2006年03月24日12点02分54秒
# 2. 20060324120254 => 2006.03.24 12:02:54:
# TimeTo("20060324120254", 1)
sub TimeTo
{
	if(1==$_[1] && $_[0] =~ /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/)
	{
		return "$1年$2月$3日$4点$5分$6秒";
	}
	if(2==$_[1] && $_[0] =~ /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/)
	{
		return "$1.$2.$3 $4:$5:$6";
	}
	if(3==$_[1] && $_[0] =~ /(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/)
	{
		my @date = localtime(timelocal($6,$5,$4,$3,$2-1,$1));
		return "$1年$2月$3日$4点$5分 $WEEK[$date[6]]";
	}
	return $_[0];
}

#标记编码
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

#转换回车换行符为内部表示，UnEnter相反
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

# 转跳到url
# ChangeTo(url);
sub ChangeTo
{
	print "Location: $_[0]\n\n";
	exit(1);
}
