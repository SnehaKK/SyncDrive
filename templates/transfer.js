$(function() {
	var drop = document.querySelector('#pane1');
	addEvent(drop, 'dragover', cancel);
	addEvent(drop, 'dragenter', cancel);
	addEvent(drop, 'drop', drophandler);
	drop = document.querySelector('#pane2');
	addEvent(drop, 'dragover', cancel);
	addEvent(drop, 'dragenter', cancel);
	addEvent(drop, 'drop', drophandler);
});

var paneDrive = [-1, -1];
var labels = ["Google Drive", "SkyDrive", "Dropbox", "Box"];

function showUpload(pane) {
    if (paneDrive[parseInt(pane) - 1] == -1)
        return;
    var wstr = "";
    wstr += "<form enctype=\"multipart/form-data\" method=\"post\" action=\"/upload\">";
    wstr += "<input type=\"file\" name=\"file\" />";
    wstr += "<br/><br/>";
    wstr += "<input type=\"submit\" class=\"btn btn-primary\" value=\"Upload!\" />";
    wstr += "<input type=\"hidden\" name=\"drive\" value=\"" + paneDrive[parseInt(pane) - 1] + "\" />";
    wstr += "</form>";
    $('#modalTitle').html("Upload a file to " + labels[paneDrive[parseInt(pane) - 1]]);
    $('#modalBody').html(wstr);
    $('#modalBox').modal('show');
}

function drophandler(event) {
	var text = event.dataTransfer.getData('Text');
	var srcId = text.substring(2);
	var src = parseInt(text.substring(1,2));
	var dst = (src == 1) ? 2 : 1;
    $('#modalTitle').html("Please wait...");
    var fileName = $('#' + text).html();
    if (fileName == undefined || fileName == "undefined")
        fileName = "";
    $('#modalBody').html("Transfering <i>" + fileName + "</i> from <b>" + labels[parseInt(paneDrive[src - 1])] + "</b> to <b>" + labels[parseInt(paneDrive[dst - 1])] + "</b> ...");
    $('#modalBox').modal('show');
	$.get('/transfer_file?src=' + paneDrive[src - 1] + '&dst=' + paneDrive[dst - 1] + '&dst_pane=' + dst + '&file_id=' + srcId, function(data) {
		$('#drivePane' + dst).append(data);
        makeDraggable();
        $('#modalBox').modal('hide');
	});
}

function cancel(event) {
    if (event.preventDefault) {
        event.preventDefault();
    }
    return false;
}

function listFiles(pane, drive, folder) {
    $('#pane' + pane + 'upload').val(drive);
	paneDrive[parseInt(pane) - 1] = drive;
	$('#drivePane' + pane).html('<center><br/><img src="/static/loading.gif" /><br/><br/></center>');
	$.get('/list_files?drive=' + drive + '&folder=' + folder + '&pane=' + pane , function(data) {
		$('#drivePane' + pane).html(data);
		makeDraggable();
	});
}

function makeDraggable() {
    var dragItems = document.querySelectorAll('a');
    for (var i = 0; i < dragItems.length; i++) {
        addEvent(dragItems[i], 'dragstart', function (event) {
        event.dataTransfer.setData('Text', this.id);
      });
    }
}

function fetchPaneData(data) {
    var drive = data.selectedIndex;
    var origId = data.original[0].id + "";
    var pane = origId.charAt(4);
    listFiles(pane, drive, '');
}

var providers = [
    {
        'text': 'Google Drive',
        'value': 0,
        'selected': false,
        'description': 'Transfer files to/from Google Drive',
        'imageSrc': 'static/google-drive-32.png'
    },
    {
        'text': 'SkyDrive',
        'value': 1,
        'selected': false,
        'description': 'Transfer files to/from SkyDrive',
        'imageSrc': 'static/skydrive-32.png'
    },
    {
        'text': 'Dropbox',
        'value': 2,
        'selected': false,
        'description': 'Transfer files to/from Dropbox',
        'imageSrc': 'static/dropbox-32.png'
    },
    {
        'text': 'Box',
        'value': 3,
        'selected': false,
        'description': 'Transfer files to/from Box',
        'imageSrc': 'static/box-32.png'
    },
];

$('#pane1_drive').ddslick({
    data: providers,
    width: "260px",
    selectText: "Choose a Storage Provider",
    {% if pane1 != None %}
    defaultSelectedIndex: {{pane1}},
    {% endif %}
    onSelected: fetchPaneData
});
$('#pane2_drive').ddslick({
    data: providers,
    width: "260px",
    selectText: "Choose a Storage Provider",
    {% if pane2 != None %}
    defaultSelectedIndex: {{pane2}},
    {% endif %}
    onSelected: fetchPaneData
});
