//
// Typofinder for domain typo discovery
// 
// Released as open source by NCC Group Plc - http://www.nccgroup.com/
// 
// Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com
//
// http://www.github.com/nccgroup/typofinder
//
// Released under AGPL see LICENSE for more information#
//

// -------------------------------------
// Globals
// -------------------------------------
var intPBarMax = 0;
var intPBarCount = 0;
var domainsNoResults = [];
var masterData = null;


// -------------------------------------
//
// -------------------------------------
function isCookieSet(cookieName) {
    try
    {
        return (getCookie(cookieName) == "true" || getCookie(cookieName) == "");
    }
    catch (err)
    {
        return false;
    }
}

function getCookies() {
    // Set cookie
    try {
        document.getElementById('host').value = getCookie("typofinder-domain");
    } catch (err) {
    }

    document.getElementById('typos').checked = isCookieSet("typofinder-typos");
    document.getElementById('bitflip').checked = isCookieSet("typofinder-bitflip");
    document.getElementById('homoglyph').checked = isCookieSet("typofinder-homoglyph");
    document.getElementById('tld').checked = isCookieSet("typofinder-tlds");

    try {
        var sValue = getCookie("typofinder-typoamount");
        if(sValue != "" && getCookie("typofinder-typoamountdesc") != "" ){
            document.getElementById('typoamountdesc').value = getCookie("typofinder-typoamountdesc");
            $("#slider").slider('value', sValue);
        } else {
            $("#slider").slider('value', 100);
            document.getElementById('typoamountdesc').value = "Rigorous";
        }
    } catch (err) {
        console.log("error");
        $("#slider").slider('value', 100);
        document.getElementById('typoamountdesc').value = "Rigorous";
    }

    document.getElementById('doppelganger').checked = isCookieSet("typofinder-doppelganger");
    document.getElementById('noreg').checked = isCookieSet("typofinder-noreg");

    try {
        var sValue = getCookie("typofinder-charsetamount");
        if(sValue != "" && getCookie("typofinder-charsetamountdesc") != "" ){
            document.getElementById('charsetamountdesc').value = getCookie("typofinder-charsetamountdesc");
            $("#charsetslider").slider('value', sValue);
        } else {
            $("#charsetslider").slider('value', 100);
            document.getElementById('charsetamountdesc').value = "      All";
        }
    } catch (err) {
        console.log("error");
        $("#charsetslider").slider('value', 100);
        document.getElementById('charsetamountdesc').value = "      All";
    }

    try {
    if (getCookie("typofinder-allresults")== "true"){
        document.getElementById("allresults").selected = isCookieSet("typofinder-allresults")
    } else if (getCookie("typofinder-onlyalexa")== "true"){
        document.getElementById("onlyalexa").selected = isCookieSet("typofinder-onlyalexa")
    } else if (getCookie("typofinder-neveralexa")== "true"){
        document.getElementById("neveralexa").selected = isCookieSet("typofinder-neveralexa")
    }
    } catch(err) {
        console.log("error");
        document.getElementById("allresults").selected = isCookieSet("typofinder-allresults")
    }
}

// -------------------------------------
// Get the original domains data
// -------------------------------------
function getMasterData() {
    var URL = "./entity.ncc";

    $.post(URL, { host: document.getElementById("host").value }, function (data) {

            masterData = data;
        })
        .fail(function (xhr, textStatus, errorThrown) {
    
        })
        .always(function (data) {
    
        }, 'json');

    intPBarCount++;
    $("#progressbar").progressbar("option", "value", intPBarCount);
}

// -------------------------------------
// This generates the accordian tag for a domain
// note: this needs to set bVal true for it to appear
// -------------------------------------
function generateTag(data) {
    var bVal = false;
    var strTag = "( ";

    // IPv4 Address
    if (data.IPv4Addresses.length > 0) {
        strTag = strTag + "IPv4 ";
        bVal = true;
    }

    // IPv6 Address
    if (data.IPv6Addresses.length > 0) {
        strTag = strTag + "IPv6 ";
        bVal = true;
    }

    // MX Records
    if (data.aMX.length > 0) {
        strTag = strTag + "MX ";
        bVal = true;
    }

    // www IPv4 Address
    if (data.wwwv4.length > 0) {
        strTag = strTag + "WWWv4 ";
        bVal = true;
    }

    // www IPv6 Address
    if (data.wwwv6.length > 0) {
        strTag = strTag + "WWWv6 ";
        bVal = true;
    }

    // m IPv4 Address
    if (data.mv4.length > 0) {
        strTag = strTag + "Mv4 ";
        bVal = true;
    }

    // m IPv6 Address
    if (data.mv6.length > 0) {
        strTag = strTag + "Mv6 ";
        bVal = true;
    }

    // webmail IPv4 Address
    if (data.webmailv4.length > 0) {
        strTag = strTag + "WebMailv4 ";
        bVal = true;
    }

    // webmail IPv6 Address
    if (data.webmailv6.length > 0) {
        strTag = strTag + "WebMailv6 ";
        bVal = true;
    }

    strTag = strTag + ")";

    // safe browsing
    if (data.SafeBrowsing.length > 0) {
        strTag = strTag + "SafeBrowsingAlert ";
        bVal = true;
    }


    if (bVal == true) return strTag;
    else {
        domainsNoResults.push(data.strDomain); // likely no longer needed
        return null;
    }
}

// -------------------------------------
// this returns an image DOM object
// for the flag for the geo of the 
// IPv4 address
// -------------------------------------
function geoIPImageIPv4(sIP, strTBL) {
    var URL = "./geov4.ncc/" + sIP;
    var img = document.createElement('img');
    img.src = URL;
    if (strTBL != null) {
        strTBL = strTBL + "<img src =\"" + URL + "\"><br/>"; // this is horrible and dangerous
    }

    return strTBL;
}

// -------------------------------------
// this returns an image DOM object
// for the flag for the geo of the 
// IPv6 address
// -------------------------------------
function geoIPImageIPv6(sIP, strTBL) {
    var URL = "./geov6.ncc/" + sIP;
    var img = document.createElement('img');
    img.src = URL;
    if (strTBL != null) {
        strTBL = strTBL + "<img src =\"" + URL + "\"><br/>"; // this is horrible and dangerous
    }

    return strTBL;
}

// -------------------------------------
// this generates the results table row contents for this domain
// -------------------------------------
function fillDetails(data) {
    var strTBLIP = ""; // used for v4 and v6 results column

    // IPv4 Address
    if (data.IPv4Addresses.length > 0) {
        for (intCount = 0; intCount < data.IPv4Addresses.length; intCount++) {
            strTBLIP = strTBLIP + "IPv4: " + data.IPv4Addresses[intCount];
            strTBLIP = geoIPImageIPv4(data.IPv4Addresses[intCount], strTBLIP);
        }
    }


    // IPv6 Address
    if (data.IPv6Addresses.length > 0) {
        for (var intCount = 0; intCount < data.IPv6Addresses.length; intCount++) {
            strTBLIP = strTBLIP + "IPv6: " + data.IPv6Addresses[intCount];
            strTBLIP = geoIPImageIPv6(data.IPv6Addresses[intCount], strTBLIP);
        }
    }

    // MX Records
    var strTBLMX = "";
    if (data.aMX.length > 0) {
        for (intCount = 0; intCount < data.aMX.length; intCount++) {
            strTBLMX = strTBLMX + data.aMX[intCount] + "<br/>";


            if (data.aMXIPv4[data.aMX[intCount]] != null) {
                for (var IP in data.aMXIPv4[data.aMX[intCount]]) {
                    strTBLMX = strTBLMX + "- IPv4: " + data.aMXIPv4[data.aMX[intCount]][IP];
                    strTBLMX = geoIPImageIPv4(data.aMXIPv4[data.aMX[intCount]][IP], strTBLMX);
                }
            }


            if (data.aMXIPv6[data.aMX[intCount]] != null) {
                for (var IP in data.aMXIPv6[data.aMX[intCount]]) {
                    strTBLMX = strTBLMX + "- IPv6: " + data.aMXIPv6[data.aMX[intCount]][IP];
                    strTBLMX = geoIPImageIPv6(data.aMXIPv6[data.aMX[intCount]][IP], strTBLMX);
                }
            }

        }
    }

    // www IPv4 Address
    var strTBLwww = "";
    if (data.wwwv4.length > 0) {
        for (intCount = 0; intCount < data.wwwv4.length; intCount++) {
            strTBLwww = strTBLwww + "IPv4: " + data.wwwv4[intCount];
            strTBLwww = geoIPImageIPv4(data.wwwv4[intCount], strTBLwww);
        }
    }

    // www IPv6 Address
    if (data.wwwv6.length > 0) {
        for (intCount = 0; intCount < data.wwwv6.length; intCount++) {
            strTBLwww = strTBLwww + "IPv6: " + data.wwwv6[intCount];
            strTBLwww = geoIPImageIPv6(data.wwwv6[intCount], strTBLwww);
        }
    }

    // m IPv4 Address
    var strTBLm = "";
    if (data.mv4.length > 0) {
        for (intCount = 0; intCount < data.mv4.length; intCount++) {
            strTBLm = strTBLm + "IPv4: " + data.mv4[intCount];
            strTBLm = geoIPImageIPv4(data.mv4[intCount], strTBLm);
        }
    }

    // m IPv6 Address
    if (data.mv6.length > 0) {
        for (intCount = 0; intCount < data.mv6.length; intCount++) {
            strTBLm = strTBLm + "IPv6: " + data.mv6[intCount];
            strTBLm = geoIPImageIPv6(data.mv6[intCount], strTBLm);
        }
    }

    // webmail IPv4 Address
    var strTBLwebmail = "";
    if (data.webmailv4.length > 0) {
        for (intCount = 0; intCount < data.webmailv4.length; intCount++) {
            strTBLwebmail = strTBLwebmail + "IPv4: " + data.webmailv4[intCount];
            strTBLwebmail = geoIPImageIPv4(data.webmailv4[intCount], strTBLwebmail);
        }
    }

    // webmail IPv6 Address
    if (data.webmailv6.length > 0) {
        for (intCount = 0; intCount < data.webmailv6.length; intCount++) {
            strTBLwebmail = strTBLwebmail + "IPv6: " + data.webmailv6[intCount];
            strTBLwebmail = geoIPImageIPv6(data.webmailv6[intCount], strTBLwebmail);
        }
    }

    var strDomain = "";

    if (document.getElementById("host").value == data.strDomain) {
        strDomain = data.strDomain + " (original)";
    } else {
        strDomain = data.strDomain;
    }

     strDomain += " " + data.tags;

    // Add the results row to the table
    $('#resultstabletable').dataTable().fnAddData(
                                                [
                                                    null,
                                                    strDomain, // domain
                                                    strTBLIP, // IP
                                                    strTBLMX, // MX
                                                    strTBLwww, // www.
                                                    strTBLwebmail, // webmail.
                                                    strTBLm, // m.
                                                    data.SafeBrowsing // safe browsing
                                                ]
                                            );

}


function unVeil() 
{

    console.log("All done");
    // Hide the progress bar
    document.getElementById("progressbar").style.display = "none";
    // Shows the original form
    document.getElementById("typogulator").style.display = "block";
    // Shows the results table
    document.getElementById("resultstable").style.display = "block";
    // Check the setting
    if (document.getElementById('noreg').checked == true) {
        // Shows the no results table   
        document.getElementById("notregtable").style.display = "block";
        // Shows the titles (we don't need to show both if the user doesn't wish to show the second
        document.getElementById("reg").style.display = "block";
        document.getElementById("unreg").style.display = "block";
    }
}
// -------------------------------------
// this is called for each domain
// to parse the JSON results
// -------------------------------------
function loadDetails(strDomain) {
    var URL = "./entity.ncc";

    //console.log("processing " + strDomain);

    $.post(URL, { host: strDomain }, function (data) {

        intPBarCount++;

        //console.log("processed " + strDomain);
        var strTag = generateTag(data);
        //console.log("got tag " + strDomain);
        if (strTag != null && data != null) {
            //console.log("filling " + strDomain);
            fillDetails(data);
            //console.log("filled " + strDomain);
        } else {
            // Add the no results row to the table
            //console.log("no results for " + strDomain);
            $('#notregtabletable').dataTable().fnAddData(
                                                [
                                                    strDomain // domain
                                                ]
                                            );
        }



        if (intPBarCount >= intPBarMax) {
            unVeil();
        } else {
            //console.log(intPBarCount + " of " + intPBarMax);
        }

        $("#progressbar").progressbar("option", "value", intPBarCount);
    })
        .fail(function (xhr, textStatus, errorThrown) {
            console.log("Error " + textStatus + " " + errorThrown + " " + strDomain);
            intPBarCount++;
            if (intPBarCount >= intPBarMax) {
                unVeil();
            } else {
                //console.log(intPBarCount + " of " + intPBarMax);
            }
            $("#progressbar").progressbar("option", "value", intPBarCount);
        })
        .always(function (data) {

        }, 'json');
}


/* Formating function for row details */
function fnFormatDetails ( oTable, nTr )
{
    var aData = oTable.fnGetData( nTr );
    var strDomain = aData[1];
    if (strDomain.indexOf(" ") > -1)
    {
        strDomain = strDomain.substr(0, strDomain.indexOf(" "));
    }

    // var sOut = '';
    var domOut = document.createDocumentFragment();

    //Links
    if (aData[2] != "" || aData[4] != "" || aData[5] != "" || aData[6] != "")
    {
        // sOut += '<h5>Links (be careful!):</h5>';
        var domH5 = document.createElement('h5');
        domH5.innerText = "Links (be careful!)";
		domH5.textContent = "Links (be careful!)";
        domOut.appendChild(domH5);

        // sOut += '<table cellpadding="5" cellspacing="0" border="0">';
        var domTBL = document.createElement("table");
        domTBL.setAttribute('cellpadding', '5');
        domTBL.setAttribute('cellspacing', '0');
        domTBL.setAttribute('border', '0');


        if (aData[2] != "")
        {
            var domTR = document.createElement('tr');
            domTBL.appendChild(domTR);

            var domTD = document.createElement('td');
            domTR.appendChild(domTD);

            var aLink = document.createElement('a');
            aLink.href = "http://" + strDomain;
            aLink.addEventListener('click',
                function (event) {
                    event.preventDefault();
                    window.open(this.href);
                },
            false);
            aLink.innerText = strDomain;
			aLink.textContent = strDomain;

            domTD.appendChild(aLink);
        }
        if (aData[4] != "")
        {
            var domTR = document.createElement('tr');
            domTBL.appendChild(domTR);

            var domTD = document.createElement('td');
            domTR.appendChild(domTD);

            var aLink = document.createElement('a');
            aLink.href = "http://www." + strDomain;
            aLink.addEventListener('click',
                function (event) {
                    event.preventDefault();
                    window.open(this.href);
                },
            false);
            aLink.innerText = "www." + strDomain;
			aLink.textContent = "www." + strDomain;
			
            domTD.appendChild(aLink);
        }
        if (aData[5] != "")
        {
            var domTR = document.createElement('tr');
            domTBL.appendChild(domTR);

            var domTD = document.createElement('td');
            domTR.appendChild(domTD);

            var aLink = document.createElement('a');
            aLink.href = "http://webmail." + strDomain;
            aLink.addEventListener('click',
                function (event) {
                    event.preventDefault();
                    window.open(this.href);
                },
            false);
            aLink.innerText = "webmail." + strDomain;
			aLink.textContent = "webmail." + strDomain;
			
            domTD.appendChild(aLink);
        }
        if (aData[6] != "")
        {
            var domTR = document.createElement('tr');
            domTBL.appendChild(domTR);

            var domTD = document.createElement('td');
            domTR.appendChild(domTD);

            var aLink = document.createElement('a');
            aLink.href = "http://m." + strDomain;
            aLink.addEventListener('click',
                function (event) {
                    event.preventDefault();
                    window.open(this.href);
                },
            false);
            aLink.innerText = "m." + strDomain;
			aLink.textContent = "m." + strDomain;
			
            domTD.appendChild(aLink);
        }
        
        // sOut += '</table>';
        domOut.appendChild(domTBL);
    }

    //Whois
    var domH5Whois = document.createElement('h5');
    domH5Whois.innerText = "WHOIS Data:";
	domH5Whois.textContent = "WHOIS Data:";
    domOut.appendChild(domH5Whois);

    var domPre = document.createElement('pre');
    domPre.setAttribute('class', 'whois');
    domPre.innerText = "Loading...\r\n\r\n";
	domPre.textContent = "Loading...\r\n\r\n";
    domOut.appendChild(domPre);

    $.ajax({
      url: "whois.ncc/"+strDomain
    })
    .done(function( msg ) {
      oTable.$(nTr).next().find(".whois").text(msg);
    });

    return domOut;
}

var oTable;

// -------------------------------------
// Ready event (i.e. entry point)
// http://gilbert.pellegrom.me/html-forms-to-ajax-forms-the-easy-way/
// -------------------------------------
$(document).ready(function () {

    // init the slider
    $("#slider").slider({
        value: 100,
        min: 0,
        max: 100,
        step: 50,
        slide: function (event, ui) {
            $("#typoamount").val(ui.value);
            if (ui.value < 50) {
                $("#typoamountdesc").val("   Quick");
            }
            else if (ui.value < 100) {
                $("#typoamountdesc").val("Balanced");
            }
            else {
                $("#typoamountdesc").val("Rigorous");
            }
        }
    });
    $("#typoamountdesc").val("Rigorous");

    // init the other slider
    $("#charsetslider").slider({
        value: 100,
        min: 0,
        max: 100,
        step: 50,
        slide: function (event, ui) {
            $("#charsetamount").val(ui.value);
            if (ui.value < 50) {
                $("#charsetamountdesc").val("    ASCII");
            }
            else if (ui.value < 100) {
                $("#charsetamountdesc").val("  rfc3491");
            }
            else {
                $("#charsetamountdesc").val("      All");
            }
        }
    });
    $("#charsetamountdesc").val("      All");

    // init the progressbar
    $("#progressbar").progressbar({
        value: 0
    });

    // init the data table
    oTable = $('#resultstabletable').dataTable({
        "iDisplayLength": 100,
        "lengthMenu": [ [25, 50, 100, -1], [25, 50, 100, "All"] ],
        "columnDefs": [
            { "orderable": false, "targets": 0 }
        ],
        "order": [ 1, 'asc' ],
        "fnCreatedRow": function (nRow, aData, iDataIndex) {
            $('td:first', nRow).html('<img src="images/add.png">');

            /* Add event listener for opening and closing details
            * Note that the indicator for showing which row is open is not controlled by DataTables,
            * rather it is done here
            */
            $('td:first-of-type img', nRow).on('click', function () {
                var nTr = $(this).parents('tr')[0];
                if (oTable.fnIsOpen(nTr)) {
                    /* This row is already open - close it */
                    this.src = "images/add.png";
                    oTable.fnClose(nTr);
                }
                else {
                    /* Open this row */
                    this.src = "images/minus.png";
                    oTable.fnOpen(nTr, fnFormatDetails(oTable, nTr), 'details');
                    /* Ensure that the new row is as wide as the table is now that it has the extra details column */
                    var newrow = $(this).closest("tr").next("tr").children("td");
                    newrow.attr("colspan", parseInt(newrow.attr("colspan")) + 1);
                }
            });
        }
    });

    // init the data table
    $('#notregtabletable').dataTable({
        "iDisplayLength": 100,
        "lengthMenu": [ [25, 50, 100, -1], [25, 50, 100, "All"] ],
        "ordering": false
    });

    // Hide the progressbar
    document.getElementById("progressbar").style.display = "none";

    //Autofocus the search box
    $("#host").focus();

    // Read the cookie values if present from a previous session
    getCookies();

    // Submit function processing
    $("#typogulator").submit(function () {

        // Input validation
        var strHost = document.getElementById('host').value;
        if (strHost.indexOf('.') == -1) {
            document.getElementById('host').value = document.getElementById('host').value + ".com";
        }

        // Hide the form
        document.getElementById("typogulator").style.display = "none";
        // Hide the results table
        document.getElementById("resultstable").style.display = "none";
        // Hide the results table
        document.getElementById("notregtable").style.display = "none";
        // Shows the title
        document.getElementById("reg").style.display = "none";
        document.getElementById("unreg").style.display = "none";
        // Reset and show the progress bar
        intPBarCount = 0;
        $("#progressbar").progressbar("option", "value", 0);
        document.getElementById("progressbar").style.display = "block";
        // Reset the list of domains which didn't yield results 
        domainsNoResults = [];
        // Reset the table
        $('#resultstabletable').dataTable()._fnClearTable();
        // Reset the no results table
        $('#notregtabletable').dataTable()._fnClearTable();

        // Set cookie
        try {
            setCookie("typofinder-domain", document.getElementById('host').value, 365);
        } catch (err) {
            setCookie("typofinder-domain", "false", 365);
        }

        try {
            setCookie("typofinder-typos", document.getElementById('typos').checked, 365);
        } catch (err) {
            setCookie("typofinder-typos", "false", 365);
        }

        try {
            setCookie("typofinder-bitflip", document.getElementById('bitflip').checked, 365);
        } catch (err) {
            setCookie("typofinder-bitflip", "false", 365);
        }

        try {
            setCookie("typofinder-homoglyph", document.getElementById('homoglyph').checked, 365);
        } catch (err) {
            setCookie("typofinder-homoglyph", "false", 365);
        }

        try {
            setCookie("typofinder-tlds", document.getElementById('tld').checked, 365);
        } catch (err) {
            setCookie("typofinder-tlds", "false", 365);
        }

        try {
            setCookie("typofinder-typoamount", $('#slider').slider("option", "value"), 365);
        } catch (err) {
            setCookie("typofinder-typoamount", 100, 365);
            setCookie("typofinder-typoamountdesc", "Rigorous", 365);
        }

        try {
            setCookie("typofinder-typoamountdesc", document.getElementById('typoamountdesc').value, 365);
        } catch (err) {
            setCookie("typofinder-typoamount", 100, 365);
            setCookie("typofinder-typoamountdesc", "Rigorous", 365);
        }

        try {
            setCookie("typofinder-doppelganger", document.getElementById('doppelganger').checked, 365);
        } catch (err) {
            setCookie("typofinder-doppelganger", false, 365);
        }

        try {
            setCookie("typofinder-noreg", document.getElementById('noreg').checked, 365);
        } catch (err) {
            setCookie("typofinder-noreg", false, 365);
        }

        try {
            setCookie("typofinder-charsetamount", $('#charsetslider').slider("option", "value"), 365);
        } catch (err) {
            setCookie("typofinder-charsetamount", 100, 365);
            setCookie("typofinder-charsetamountdesc", "      All", 365);
        }

        try {
            setCookie("typofinder-charsetamountdesc", document.getElementById('charsetamountdesc').value, 365);
        } catch (err) {
            setCookie("typofinder-charsetamount", 100, 365);
            setCookie("typofinder-charsetamountdesc", "      All", 365);
        }

        try {
                setCookie("typofinder-allresults", document.getElementById('allresults').selected, 365);
                setCookie("typofinder-onlyalexa", document.getElementById('onlyalexa').selected, 365);
                setCookie("typofinder-neveralexa", document.getElementById('neveralexa').selected, 365);
        } catch (err) {
            setCookie("typofinder-allresults", document.getElementById('allresults'), true, 365);
        }

        //Do the AJAX post
        var typogulator = $("#typogulator");
        $.post(typogulator.attr("action"), typogulator.serialize(), function (data) {

            // max for the progress bar
            intPBarMax = data.length + 1; // we add one to factor in the first request

            // set the max on the progress bar
            $("#progressbar").progressbar("option", "max", data.length);

            // Get the original domains data
            getMasterData();

            // now loop through and process them
            for (var key in data) {
                // the success function
                loadDetails(data[key]);
            }


        })
            .fail(function (xhr, textStatus, errorThrown) {
                console.log("error " + textStatus);
                document.getElementById("progressbar").style.display = "none";
                document.getElementById("resultstable").style.display = "none";
                document.getElementById("notregtabletable").style.display = "none";
                document.getElementById("typogulator").style.display = "block";
            })
            .always(function (data) {
                //console.log(data)
            }, 'json');

        //Important. Stop the normal POST
        return false;
    });
});
