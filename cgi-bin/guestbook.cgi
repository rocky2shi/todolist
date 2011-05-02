#!/usr/bin/perl
##########################################################
#                                                        #
#   ����: rocky                                          #
#   QQ  : 15586350                                       #
#   ����: ���Ա�                                         #
#   �汾: 091                                            #
#                                                        #
##########################################################

require "common.pl";

my $GUEST_BOOK = "$DATA_DIR/guest_book.txt";

# ��������
sub SubmitSave
{
    my %data = ();
    ReadFile($GUEST_BOOK, \%data);
    $data{$KEYSTRING}{visitor}  = $in{visitor};
    $data{$KEYSTRING}{content}  = Enter( $in{content} );
    $data{$KEYSTRING}{time}     = TimeTo($KEYSTRING, 2);
    WriteFile($GUEST_BOOK, \%data);
    ChangeTo("$ENV{SCRIPT_NAME}");
}

##############################################################################

# ���ύ�����ݵ�%in��
ParseSubmit(\%in);


SubmitSave() if($in{submit});














##############################################################################



print "Content-type: text/html\n\n";

# ��д����
if($in{opr} eq "say")
{
print <<eof;
<html>
<head>
<title>���Ա�</title>
<style>
body,p{
    font-family: "Arial", "Helvetica", "sans-serif";
    font-style: normal;
    color:#626262;
    font-size:15px;
    background: url("");
}

pre{
    margin-left:210px;
}
#visitor{
    width:249px;
}
#content{
    width:500px;
    height:300;
}
</style>

<body>

<h2>���Ա�</h2>
<hr>
<br>

<form method="POST" action="guestbook.cgi">
������<input id="visitor" name="visitor" class="NOTEMPTY"><br><br>
���ݣ�<br>
������<textarea id="content" name="content" wrap="VIRTUAL"></textarea>��
      <input type="submit" name="submit" value="�ύ">
</form>

</body>
</html>
eof

}

# ����Ա
elsif($in{opr} eq 'manage')
{
    print "�����У�����[<a href='javascript:history.back()'>����</a>]";
}

# ��ʾ��������
else
{

ReadFile($GUEST_BOOK, \%data);

print <<eof;
<html>
<title>���Ա�</title>
<style>
body,p{
    font-family: "Arial", "Helvetica", "sans-serif";
    font-style: normal;
    color:#000000;
    font-size:15px;
}

pre{
    margin-left:1px;
}

legend{
    color:#000000;
}

.color1{
    color:#000000;
}
</style>

<h1>���Ա�</h1>
<hr>
<a href="$ENV{SCRIPT_NAME}?opr=say">��Ҫ����</a>    <a href="$ENV{SCRIPT_NAME}?opr=manage">����Ա</a>
<br>
eof


$index = 0;
foreach $item ( sort cmpAB keys %data )
{
    $index = sprintf("%d", ++$index);
    my $content = Escape($data{$item}{content});
    $content = UnEnter($content);
    print <<eof;
<fieldset>
<legend><span class="color1">[$index¥]</span> $data{$item}{time}��$data{$item}{visitor}</legend>
<pre>
$content
</pre>
</fieldset>
<br>

eof
}


}
