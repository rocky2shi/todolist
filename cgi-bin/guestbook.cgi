#!/usr/bin/perl
##########################################################
#                                                        #
#   作者: rocky                                          #
#   QQ  : 15586350                                       #
#   功能: 留言本                                         #
#   版本: 091                                            #
#                                                        #
##########################################################

require "common.pl";

my $GUEST_BOOK = "$DATA_DIR/guest_book.txt";

# 保存留言
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

# 读提交的数据到%in中
ParseSubmit(\%in);


SubmitSave() if($in{submit});














##############################################################################



print "Content-type: text/html\n\n";

# 填写留言
if($in{opr} eq "say")
{
print <<eof;
<html>
<head>
<title>留言本</title>
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

<h2>留言本</h2>
<hr>
<br>

<form method="POST" action="guestbook.cgi">
姓名：<input id="visitor" name="visitor" class="NOTEMPTY"><br><br>
内容：<br>
　　　<textarea id="content" name="content" wrap="VIRTUAL"></textarea>　
      <input type="submit" name="submit" value="提交">
</form>

</body>
</html>
eof

}

# 管理员
elsif($in{opr} eq 'manage')
{
    print "建设中．．．[<a href='javascript:history.back()'>返回</a>]";
}

# 显示留言数据
else
{

ReadFile($GUEST_BOOK, \%data);

print <<eof;
<html>
<title>留言本</title>
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

<h1>留言本</h1>
<hr>
<a href="$ENV{SCRIPT_NAME}?opr=say">我要留言</a>    <a href="$ENV{SCRIPT_NAME}?opr=manage">管理员</a>
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
<legend><span class="color1">[$index楼]</span> $data{$item}{time}－$data{$item}{visitor}</legend>
<pre>
$content
</pre>
</fieldset>
<br>

eof
}


}
