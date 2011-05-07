#!/usr/bin/perl
##########################################################
#                                                        #
#   ��д: Rocky 2010-11-19 11:47:04                      #
#   QQ  : 15586350                                       #
#   ����: �������                                       #
#   �汾: 0.1                                            #
#                                                        #
##########################################################

require "common.pl";
use Time::HiRes qw(gettimeofday);

# ���ݼ�¼�ļ�
my $DATA_FILE = "$DATA_DIR/todolist.txt";

# �����޸ļ�¼�ļ�
my $LAST_MODIFY = "$DATA_DIR/todolist_modify.txt";

# ��ǰϵͳ��ȷʱ��
my $TIME_USEC = gettimeofday();


# ������ǰ��¼
ReadFile($DATA_FILE, \%data);


# ����
sub SubmitSave
{
    my %data = ();
    my $id = $in{task_id} || $KEYSTRING;   # ǰ̨������id���½�

    ReadFile($DATA_FILE, \%data);

    # ���������ã���Ϊ�ٳ�������
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
        # �����������ݣ���Ϊɾ��������
        delete $data{$id};
    }

    WriteFile($DATA_FILE, \%data);

    ChangeTo("$ENV{SCRIPT_NAME}");
}

# ������ɶ�
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

    # �����޸ļ�¼
    open(FILE, ">>$LAST_MODIFY") or die("$!: $LAST_MODIFY");
    print FILE "$TIME_USEC $id\n";
    close(FILE);

    ChangeTo("$ENV{SCRIPT_NAME}");
}

# ȡ�б䶯����Ŀ
sub GetLastModify
{
    print "Content-type: text/html\n\n";

    # ҳ���ϴ��������ˢ��ʱ��
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

        # �����ɼ�¼
        next if($t < $web_last_refresh);

        $list .= "{'id':'$id','value':'$value'},";
    }
    close(FILE);

    if($list ne "")
    {
        Debug("$list");

        # ����json��
        print <<eof;
        {
            "last_refresh":"$TIME_USEC",
            "modify":[$list]
        }
eof
    }

    exit;
}



$SortSequence = ""; # �����������������л���
$pSortFunc = sub{};
%SortMark = ();     # �����ǣ���ҳ����ͷ��ʾһ��¼��ָ����ǰ�������ֶΣ�

#
# ��������
#
sub SetSort
{
    #
    # ��ascii��������
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
    # �������
    #
    my $mark = '^';
    my $pSortSequence = sub{};
    if($in{SortSequence} eq "rise")
    {
        $pSortSequence = sub{
            &$pSortType($_[0], $_[1]);
        };
        $SortSequence = "drop";
        $mark = '<span title="��ǰΪ��������">��</span>';
    }
    else
    {
        $pSortSequence = sub{
            &$pSortType($_[1], $_[0]);
        };
        $SortSequence = "rise";
        $mark = '<span title="��ǰΪ��������">��</span>';
    }


    #
    # ָ��������
    #
    if($in{SortFunc} eq "task_name")
    {
        # ������������
        $pSortFunc = sub{
            my $x1 = $data{$a}{name};
            my $x2 = $data{$b}{name};
            &$pSortSequence($x1, $x2);
        };
        $SortMark{task_name} = "$mark";
    }
    elsif($in{SortFunc} eq "task_person")
    {
        # ������������
        $pSortFunc = sub{
            my $x1 = $data{$a}{person} || 'δ����';
            my $x2 = $data{$b}{person} || 'δ����';
            &$pSortSequence($x1, $x2);
        };
        $SortMark{task_person} = "$mark";
    }
    elsif($in{SortFunc} eq "task_set_progress")
    {
        # ����ɶ�����
        $pSortFunc = sub{
            my $x1 = $data{$a}{progress} || '0';
            my $x2 = $data{$b}{progress} || '0';
            &$pSortSequence($x1, $x2);
        };
        $SortMark{task_set_progress} = "$mark";
    }
    else
    {
        # ��ʱ������
        $pSortFunc = sub{$a cmp $b};
        #$SortMark{task_index} = "$mark";
    }
}





##############################################################################

# ���ύ�����ݵ�%in��
ParseSubmit(\%in);


SubmitSave() if($in{task_add});
SetProgress() if($in{task_set_progress});
GetLastModify() if($in{last_refresh});



SetSort();





##############################################################################



print "Content-type: text/html\n\n";



print <<eof;
<html>
<title>�������</title>
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

/* ��������� */
.finish{
    text-decoration: line-through;
    font-style: oblique;
    color: #BDBDBD;
}
</style>


<script src='common.js'></script>
<script>
// ���б��е�ֵcopy���޸���
function Modify(id)
{
    var list_task = document.getElementById(id).getElementsByTagName('td');
    var form_add = document.getElementById('form_add');

    // ע��list_task�е��±꣨��ҳ���������Ӧ��
    form_add["task_id"].value       = id;
    form_add["task_name"].value     = list_task[1].innerHTML;
    form_add["task_content"].value  = list_task[2].innerHTML.replace(/<pre>|<\\\/pre>/ig, '');
    form_add["task_person"].value   = list_task[3].innerHTML;
    form_add["task_progress"].value = list_task[4].innerHTML;
}

// ��ʱ���ҳ��ı仯���޸ģ�
function Timer()
{
    // ��⵱ǰ��¼�Ƿ�����Ч  [Rocky 2010-05-29 18:27:54]
    Timer.Ping = function()
    {
        var url = "todolist.cgi";

        /* ��װPost����
         */
        var post = "last_refresh=" + GetObj("last_refresh").value;

        // �������󵽷����
        SubmitToServer(url, post, Response);
        // �����Ӧ
        function Response(str)
        {
            if("" == str)
            {
                return;
            }
            // Alert(str);
            /*
             * ���صĸ�ʽ�磺
             *  {
             *      "last_refresh":"1290157544.7246",
             *      "modify":[{'id':'20101119145545','value':'checked'},{'id':'20101119151047','value':''},]
             *  }
             */
            var last_modify;
            eval("last_modify=" + str);

            // ����ҳ���ϼ�¼�����ˢ��ʱ��
            GetObj("last_refresh").value = last_modify.last_refresh;

            // ���µڸ����޸ĵ���Ŀ
            for(var i=0; i<last_modify.modify.length; i++)
            {
                var id = last_modify.modify[i].id;
                var value = last_modify.modify[i].value;
                var box = GetObj(id).getElementsByTagName("input")[2];
                // ������ƣ�ȷ�����������checkboxԪ�أ�
                if("task_progress" != box.name)
                {
                    Alert("���������checkbox: " + box.name);
                    return;
                }
                box.checked = (value == "checked" ? true : false);
            }
        }
    }

    // ������ʱ����ÿn����һ�μ��
    window.setInterval("Timer.Ping()", 1000);
}



</script>




<body onload=Timer()>
<h1>�������</h1>
<hr>

<!-- ���ˢ��ʱ�� -->
<input type="hidden" id="last_refresh" value="$TIME_USEC">


<!-- �����б� -->
<a name="top">
<table border=1>
    <tr class="center nobr">
        <th><a href="todolist.cgi" title="��������ʱ������">���</a> $SortMark{task_index}</th>
        <th><a href="todolist.cgi?SortFunc=task_name&SortSequence=$SortSequence" title="�������">��������</a> $SortMark{task_name}</th>
        <th>��������</th>
        <th><a href="todolist.cgi?SortFunc=task_person&SortSequence=$SortSequence" title="�������">������</a> $SortMark{task_person}</th>
        <th><a href="todolist.cgi?SortFunc=task_set_progress&SortSequence=$SortSequence&SortType=digit" title="�������">�����</a> $SortMark{task_set_progress}</th>
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
        <td class="center hand" title="����޸ģ�$modify" onclick="Modify('$item')">$index</td>
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
        <td align="center">����<br>/<br>�޸�<br>/<br>ɾ��</td>
        <td><input type="" name="task_name"></td>
        <td><textarea name="task_content" wrap="VIRTUAL" rows="8" cols="60"></textarea></td>
        <td><input type="" name="task_person" size="5"></td>
        <td><input type="submit" name="task_add" value="�ύ">
            <input type="reset" value="���"></td>
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
