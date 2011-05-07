#!/usr/bin/perl
##########################################################
#                                                        #
#   编写: Rocky 2010-11-19 11:47:04                      #
#   QQ  : 15586350                                       #
#   功能: 任务管理                                       #
#   版本: 0.1                                            #
#                                                        #
##########################################################

require "common.pl";
use Time::HiRes qw(gettimeofday);

# 数据记录文件
my $DATA_FILE = "$DATA_DIR/todolist.txt";

# 最新修改记录文件
my $LAST_MODIFY = "$DATA_DIR/todolist_modify.txt";

# 当前系统精确时间
my $TIME_USEC = gettimeofday();


# 读出当前记录
ReadFile($DATA_FILE, \%data);


# 保存
sub SubmitSave
{
    my %data = ();
    my $id = $in{task_id} || $KEYSTRING;   # 前台不传来id则新建

    ReadFile($DATA_FILE, \%data);

    # 不设置名置，则为操除操作；
    if($in{task_name} ne "")
    {
        $data{$id}{person}  = $in{task_person};
        $data{$id}{name}  = $in{task_name};
        $data{$id}{content} = Enter( $in{task_content} );
        $data{$id}{progress}= $in{task_progress};
        $data{$id}{modify}  = $KEYSTRING;
    }
    else
    {
        # 不填任务内容，则为删除操作；
        delete $data{$id};
    }

    WriteFile($DATA_FILE, \%data);

    ChangeTo("$ENV{SCRIPT_NAME}");
}

# 设置完成度
sub SetProgress
{
    return if($in{task_id} eq "");

    my %data = ();
    my $id = $in{task_id};

    #Debug("\$in{task_progress}=$in{task_progress}");

    ReadFile($DATA_FILE, \%data);
    if( ! exists($data{$id}) )
    {
        Debug("Task not exist, id=$id");
        return;
    }
    $data{$id}{progress}= $in{task_progress};
    $data{$id}{modify}  = $KEYSTRING;
    WriteFile($DATA_FILE, \%data);

    # 记下修改记录
    open(FILE, ">>$LAST_MODIFY") or die("$!: $LAST_MODIFY");
    print FILE "$TIME_USEC $id\n";
    close(FILE);

    ChangeTo("$ENV{SCRIPT_NAME}");
}

# 取有变动的条目
sub GetLastModify
{
    print "Content-type: text/html\n\n";

    # 页面上传来的最后刷新时间
    my $web_last_refresh = $in{last_refresh};
    my $list = "";

    open(FILE, "<$LAST_MODIFY") or die("$!: $LAST_MODIFY");
    while( <FILE> )
    {
        chomp();
        /([0-9.]+) ([0-9.]+)/;
        my $t = $1;
        my $id = $2;
        my $value = $data{$id}{progress} ? "checked" : "";

        # 跳过旧记录
        next if($t < $web_last_refresh);

        $list .= "{'id':'$id','value':'$value'},";
    }
    close(FILE);

    if($list ne "")
    {
        Debug("$list");

        # 构造json格串
        print <<eof;
        {
            "last_refresh":"$TIME_USEC",
            "modify":[$list]
        }
eof
    }

    exit;
}



$SortSequence = ""; # 用于升、降序来回切换；
$pSortFunc = sub{};
%SortMark = ();     # 排序标记（在页面表格头显示一记录，指明当前的排序字段）

#
# 排序设置
#
sub SetSort
{
    #
    # 按ascii或数排序
    #
    my $pSortType = sub{};
    if($in{SortType} eq "digit")
    {
        $pSortType = sub{
            $_[0] <=> $_[1];
        };
    }
    else
    {
        $pSortType = sub{
            $_[0] cmp $_[1];
        };
    }

    #
    # 升序或降序
    #
    my $mark = '^';
    my $pSortSequence = sub{};
    if($in{SortSequence} eq "rise")
    {
        $pSortSequence = sub{
            &$pSortType($_[0], $_[1]);
        };
        $SortSequence = "drop";
        $mark = '<span title="当前为升序排列">↑</span>';
    }
    else
    {
        $pSortSequence = sub{
            &$pSortType($_[1], $_[0]);
        };
        $SortSequence = "rise";
        $mark = '<span title="当前为降序排列">↓</span>';
    }


    #
    # 指定排序函数
    #
    if($in{SortFunc} eq "task_name")
    {
        # 按任务名排序
        $pSortFunc = sub{
            my $x1 = $data{$a}{name};
            my $x2 = $data{$b}{name};
            &$pSortSequence($x1, $x2);
        };
        $SortMark{task_name} = "$mark";
    }
    elsif($in{SortFunc} eq "task_person")
    {
        # 按负责人排序
        $pSortFunc = sub{
            my $x1 = $data{$a}{person} || '未安排';
            my $x2 = $data{$b}{person} || '未安排';
            &$pSortSequence($x1, $x2);
        };
        $SortMark{task_person} = "$mark";
    }
    elsif($in{SortFunc} eq "task_set_progress")
    {
        # 按完成度排序
        $pSortFunc = sub{
            my $x1 = $data{$a}{progress} || '0';
            my $x2 = $data{$b}{progress} || '0';
            &$pSortSequence($x1, $x2);
        };
        $SortMark{task_set_progress} = "$mark";
    }
    else
    {
        # 按时间排序
        $pSortFunc = sub{$a cmp $b};
        #$SortMark{task_index} = "$mark";
    }
}





##############################################################################

# 读提交的数据到%in中
ParseSubmit(\%in);


SubmitSave() if($in{task_add});
SetProgress() if($in{task_set_progress});
GetLastModify() if($in{last_refresh});



SetSort();





##############################################################################



print "Content-type: text/html\n\n";



print <<eof;
<html>
<title>任务管理</title>
<style>
body,p{
    font-family: "Arial", "Helvetica", "sans-serif";
    font-style: normal;
    color:#000000;
    background-color: #EEF4ED;
    font-size:15px;
}

.center{
    text-align: center;
}

.nobr{
    white-space: nowrap;
}

.hand{
    cursor: pointer;
}

/* 已完成项风格 */
.finish{
    text-decoration: line-through;
    font-style: oblique;
    color: #BDBDBD;
}
</style>


<script src='common.js'></script>
<script>
// 把列表中的值copy到修改域
function Modify(id)
{
    var list_task = document.getElementById(id).getElementsByTagName('td');
    var form_add = document.getElementById('form_add');

    // 注意list_task中的下标（和页面设置相对应）
    form_add["task_id"].value       = id;
    form_add["task_name"].value     = list_task[1].innerHTML;
    form_add["task_content"].value  = list_task[2].innerHTML.replace(/<pre>|<\\\/pre>/ig, '');
    form_add["task_person"].value   = list_task[3].innerHTML;
    form_add["task_progress"].value = list_task[4].innerHTML;
}

// 定时检查页面的变化（修改）
function Timer()
{
    // 检测当前登录是否乃有效  [Rocky 2010-05-29 18:27:54]
    Timer.Ping = function()
    {
        var url = "todolist.cgi";

        /* 组装Post参数
         */
        var post = "last_refresh=" + GetObj("last_refresh").value;

        // 发送请求到服务端
        SubmitToServer(url, post, Response);
        // 处理回应
        function Response(str)
        {
            if("" == str)
            {
                return;
            }
            // Alert(str);
            /*
             * 返回的格式如：
             *  {
             *      "last_refresh":"1290157544.7246",
             *      "modify":[{'id':'20101119145545','value':'checked'},{'id':'20101119151047','value':''},]
             *  }
             */
            var last_modify;
            eval("last_modify=" + str);

            // 更新页面上记录的最后刷新时间
            GetObj("last_refresh").value = last_modify.last_refresh;

            // 更新第个有修改的条目
            for(var i=0; i<last_modify.modify.length; i++)
            {
                var id = last_modify.modify[i].id;
                var value = last_modify.modify[i].value;
                var box = GetObj(id).getElementsByTagName("input")[2];
                // 检查名称，确保这是所需的checkbox元素；
                if("task_progress" != box.name)
                {
                    Alert("不是所需的checkbox: " + box.name);
                    return;
                }
                box.checked = (value == "checked" ? true : false);
            }
        }
    }

    // 启动定时器，每n秒做一次检测
    window.setInterval("Timer.Ping()", 1000);
}



</script>




<body onload=Timer()>
<h1>任务管理</h1>
<hr>

<!-- 最后刷新时间 -->
<input type="hidden" id="last_refresh" value="$TIME_USEC">


<!-- 任务列表 -->
<a name="top">
<table border=1>
    <tr class="center nobr">
        <th><a href="todolist.cgi" title="按任务建立时间排序">序号</a> $SortMark{task_index}</th>
        <th><a href="todolist.cgi?SortFunc=task_name&SortSequence=$SortSequence" title="点击排序">任务名称</a> $SortMark{task_name}</th>
        <th>任务内容</th>
        <th><a href="todolist.cgi?SortFunc=task_person&SortSequence=$SortSequence" title="点击排序">负责人</a> $SortMark{task_person}</th>
        <th><a href="todolist.cgi?SortFunc=task_set_progress&SortSequence=$SortSequence&SortType=digit" title="点击排序">已完成</a> $SortMark{task_set_progress}</th>
    </tr>
eof


$index = 0;
foreach $item ( sort $pSortFunc keys %data )
{
    $index = sprintf("%d", ++$index);
    my $name   = $data{$item}{name} || "";
    my $content  = UnEnter( Escape($data{$item}{content}) ) || "";
    my $person   = $data{$item}{person} || '-';
    my $progress = $data{$item}{progress} eq "" ? "" : " checked";
    my $modify   = TimeTo($data{$item}{modify}, 2);
    my $finish_style = $data{$item}{progress} eq "" ? '' : 'class="finish"';

    print <<eof;

    <tr id="$item" $finish_style>
        <form method="GET" action="todolist.cgi">
        <input type="hidden" name="task_id" value="$item">
        <input type="hidden" name="task_set_progress" value="1">
        <td class="center hand" title="最后修改：$modify" onclick="Modify('$item')">$index</td>
        <td>$name</td>
        <td><pre>$content</pre></td>
        <td class="center">$person</td>
        <td class="center"><input type="checkbox"  name="task_progress" value="100" onclick="this.form.submit()" $progress></td>
        </form>
    </tr>

eof
}



print <<eof;
    <tr>
        <td colspan="5"> </td>
    </tr>
    <tr>
        <form id="form_add" method="GET" action="todolist.cgi#end">
        <input type="" name="task_id" style="display:none;">
        <td align="center">新增<br>/<br>修改<br>/<br>删除</td>
        <td><input type="" name="task_name"></td>
        <td><textarea name="task_content" wrap="VIRTUAL" rows="8" cols="60"></textarea></td>
        <td><input type="" name="task_person" size="5"></td>
        <td><input type="submit" name="task_add" value="提交">
            <input type="reset" value="清空"></td>
        </form>
    </tr>
</table>
<a name="end">
<br>
<br>
<div align="right"><font color="#BDBDBD"><i>Rocky, 2011-4, rocky2shi\@126.com, QQ15586350</i></font></div>
</body>
</html>
eof
