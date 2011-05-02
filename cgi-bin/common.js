


/*
 *  ���ܣ���дalert()���������
 *  ��д��Rocky 2009-12-07
 */
function Alert(/* �ɱ���� */)
{
    Alert.i = (Alert.i || 0) + 1;
    alert('----------[' + Alert.i + ']----------\r\n' + '******[' + [].slice.call(arguments).join(']\r\n******[') + ']');
}

/*
 *  ���ܣ����ݿؼ�id���ؿؼ�����
 */
function GetObj(id)
{
    return document.getElementById(id);
}

/*
 * ���ܣ������������
 * ��д��Rocky 2009-11-28
 */
function CreateXmlRequest()
{
    var xmlHttp;
    if (window.ActiveXObject)
    {
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    else if (window.XMLHttpRequest)
    {
        xmlHttp = new XMLHttpRequest();
    }
    else
    {
        alert("LoadCatchphrase::() ����");
        return null;
    }
    return xmlHttp;
}

/*
 * ���ܣ���������server���̶�ΪPOST��ʽ��
 * ��д��Rocky 2009-12-02 17:23:39
 * ע�⣺���ú���ǰ��Ӧ����content�Ƿ���Ҫ encodeURIComponent()
 */
function SubmitToServer(url, content, callback)
{
    var xmlHttp = CreateXmlRequest();
    var method = "post";
    var asyn = true; // Ĭ�ϣ�true��Ϊ�첽�����ص�����

    if("" == url || null == xmlHttp)
    {
        alert("SaveToServer()�г���");
        return;
    }

    // ��������
    function Send()
    {
        // ʹ�����������ʹÿ������ˢ�»��棻
        url += "?" + (Math.random() + "").substr(2) + "&";

        // ����
        xmlHttp.onreadystatechange = Deal;
        xmlHttp.open(method, url, asyn); // true Ϊ�첽�����ص�����
        xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xmlHttp.send(content);
    }

    // �����ص�����
    function Deal()
    {
        if(xmlHttp.readyState == 4 && xmlHttp.status == 200)
        {
            // alert( decodeURIComponent(xmlHttp.responseText) );
            if(typeof callback == 'function')
            {
                callback(xmlHttp.responseText);
            }
        }
    }

    // ִ��
    Send();
}
