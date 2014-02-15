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
var domainsNoResults = new Array();
var masterData = null;

// -------------------------------------
// Empty the results
// -------------------------------------
function emptyresults() {
    var myNode = document.getElementById("results");
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
    $("#results").accordion("refresh");
}

// -------------------------------------
// Get the original domains data
// -------------------------------------
function getMasterData() {
    var URL = "./entity.ncc";
    var strTag = " ( ";
    var intCount = 0;

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
        domainsNoResults.push(data.strDomain);
        return null;
    }
}

// -------------------------------------
// this returns an image DOM object
// for the flag for the geo of the 
// IPv4 address
// -------------------------------------
function geoIPImageIPv4(sIP, domLI, strTBL) {
    var URL = "./geov4.ncc/" + sIP;
    var img = document.createElement('img');
    img.src = URL;
    if (strTBL != null) {
        strTBL = strTBL + "<img src =\"" + URL + "\"><br/>"; // this is horrible and dangerous
    }
    domLI.appendChild(img);
    return strTBL;
}

// -------------------------------------
// this returns an image DOM object
// for the flag for the geo of the 
// IPv6 address
// -------------------------------------
function geoIPImageIPv6(sIP, domLI, strTBL) {
    var URL = "./geov6.ncc/" + sIP;
    var img = document.createElement('img');
    img.src = URL;
    if (strTBL != null) {
        strTBL = strTBL + "<img src =\"" + URL + "\"><br/>"; // this is horrible and dangerous
    }
    domLI.appendChild(img);
    return strTBL;
}

// -------------------------------------
// this generates the div contents
// for a particular domain
// -------------------------------------
function fillNoResDetails(domDiv) {
    domDiv.innerText = "The following domains yielded no results (i.e. likely not registered or potentially not valid)";
    ul = document.createElement('ul');
    domDiv.appendChild(ul);
    for (var intCount = 0; intCount < domainsNoResults.length; intCount++) {
        li = document.createElement('li');
        ul.appendChild(li);
        li.innerText = domainsNoResults[intCount];
    }
}

// -------------------------------------
// this generates the results div contents for this domain
// -------------------------------------
function fillDetails(domDiv, data) {
    var ul = null;
    var li = null;
    var ourTD = null;

    var strTBLIP = ""; // used for v4 and v6 results column

    // IPv4 Address
    if (data.IPv4Addresses.length > 0) {
        for (intCount = 0; intCount < data.IPv4Addresses.length; intCount++) {
            ul = document.createElement('ul');
            domDiv.appendChild(ul);
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "IPv4: " + data.IPv4Addresses[intCount];
            strTBLIP = strTBLIP + "IPv4: " + data.IPv4Addresses[intCount];
            strTBLIP = geoIPImageIPv4(data.IPv4Addresses[intCount], li, strTBLIP);
        }
    }


    // IPv6 Address
    if (data.IPv6Addresses.length > 0) {
        for (intCount = 0; intCount < data.IPv6Addresses.length; intCount++) {
            ul = document.createElement('ul');
            domDiv.appendChild(ul);
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "IPv6: " + data.IPv6Addresses[intCount];
            strTBLIP = strTBLIP + "IPv6: " + data.IPv6Addresses[intCount];
            strTBILP = geoIPImageIPv6(data.IPv6Addresses[intCount], li, strTBLIP);
        }
    }

    // MX Records
    var strTBLMX = "";
    if (data.aMX.length > 0) {
        for (intCount = 0; intCount < data.aMX.length; intCount++) {
            ul = document.createElement('ul');
            domDiv.appendChild(ul);
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "MX: " + data.aMX[intCount];
            strTBLMX = strTBLMX + data.aMX[intCount] + "<br/>";


            if (data.aMXIPv4[data.aMX[intCount]] != null) {
                //console.log("MX IPv4 " + data.aMX[intCount] + " - " + data.aMXIPv4[data.aMX[intCount]]);

                var ulinner = document.createElement('ul');
                li.appendChild(ulinner);

                for (IP in data.aMXIPv4[data.aMX[intCount]]) {
                    var liinner = document.createElement('li');
                    ulinner.appendChild(liinner);
                    liinner.innerText = "MX IPv4: " + data.aMXIPv4[data.aMX[intCount]][IP];
                    strTBLMX = strTBLMX + "- IPv4: " + data.aMXIPv4[data.aMX[intCount]][IP];
                    strTBLMX = geoIPImageIPv4(data.aMXIPv4[data.aMX[intCount]][IP], liinner, strTBLMX);
                    //console.log("IPv4: " + data.aMXIPv4[data.aMX[intCount]][IP]);                                   
                }
            }


            if (data.aMXIPv6[data.aMX[intCount]] != null) {
                //console.log("MX IPv6 " + data.aMX[intCount] + " - " + data.aMXIPv6[data.aMX[intCount]]);

                var ulinner = document.createElement('ul');
                li.appendChild(ulinner);

                for (IP in data.aMXIPv6[data.aMX[intCount]]) {
                    var liinner = document.createElement('li');
                    ulinner.appendChild(liinner);
                    liinner.innerText = "MX IPv6: " + data.aMXIPv6[data.aMX[intCount]][IP];
                    strTBLMX = strTBLMX + "- IPv6: " + data.aMXIPv6[data.aMX[intCount]][IP];
                    strTBLMX = geoIPImageIPv6(data.aMXIPv6[data.aMX[intCount]][IP], liinner, strTBLMX);
                    //console.log("IPv6: " + data.aMXIPv4[data.aMX[intCount]][IP]);                                   
                }
            }

        }
    }

    // www IPv4 Address
    var strTBLwww = "";
    if (data.wwwv4.length > 0) {
        ul = document.createElement('ul');
        domDiv.appendChild(ul);

        for (intCount = 0; intCount < data.wwwv4.length; intCount++) {
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "www IPv4: " + data.wwwv4[intCount];
            strTBLwww = strTBLwww + "IPv4: " + data.wwwv4[intCount]
            strTBLwww = geoIPImageIPv4(data.wwwv4[intCount], li, strTBLwww);

            // Safebrowsing
            if (data.SafeBrowsing.length > 0) {
                li.innerText = "www IPv4: " + data.wwwv6[intCount] + " - " + data.SafeBrowsing;
            }
        }

        // URL
        lilink = document.createElement('li');
        aLink = document.createElement('a');

        strHost = "http://www." + data.strDomain;
        aLink.href = strHost;
        aLink.addEventListener('click', 
            function (event) {
                event.preventDefault();
                window.open(this.href);
            },
        false);


        aLink.innerText = "link (be careful) www." + data.strDomain;
        lilink.appendChild(aLink);
        ul.appendChild(lilink);
    }

    // www IPv6 Address
    if (data.wwwv6.length > 0) {
        ul = document.createElement('ul');
        domDiv.appendChild(ul);

        for (intCount = 0; intCount < data.wwwv6.length; intCount++) {
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "www IPv6: " + data.wwwv6[intCount];
            strTBLwww = strTBLwww + "IPv6: " + data.wwwv6[intCount]
            strTBLwww = geoIPImageIPv6(data.wwwv6[intCount], li, strTBLwww);

            // Safebrowsing
            if (data.SafeBrowsing.length > 0) {
                li.innerText = "www IPv6: " + data.wwwv6[intCount] + " - " + data.SafeBrowsing;
            }

        }

        // URL
        lilink = document.createElement('li');
        aLink = document.createElement('a');
        
        strHost = "http://www." + data.strDomain;
        aLink.href = strHost;
        aLink.addEventListener('click',
            function (event) {
                event.preventDefault();
                window.open(this.href);
            },
        false);

        aLink.innerText = "link (be careful) www." + data.strDomain;
        lilink.appendChild(aLink);
        ul.appendChild(lilink);
    }

    // m IPv4 Address
    var strTBLm = "";
    if (data.mv4.length > 0) {
        ul = document.createElement('ul');
        domDiv.appendChild(ul);

        for (intCount = 0; intCount < data.mv4.length; intCount++) {
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "m IPv4: " + data.mv4[intCount];
            strTBLm = strTBLm + "IPv4 " + data.mv4[intCount];
            strTBLm = geoIPImageIPv4(data.mv4[intCount], li, strTBLm);
        }

        // URL
        lilink = document.createElement('li');
        aLink = document.createElement('a');

        strHost = "http://m." + data.strDomain;
        aLink.href = strHost;
        aLink.addEventListener('click',
            function (event) {
                event.preventDefault();
                window.open(this.href);
            },
        false);

        aLink.innerText = "link (be careful) m." + data.strDomain;
        lilink.appendChild(aLink);
        ul.appendChild(lilink);
    }

    // m IPv6 Address
    if (data.mv6.length > 0) {
        ul = document.createElement('ul');
        domDiv.appendChild(ul);

        for (intCount = 0; intCount < data.mv6.length; intCount++) {
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "m IPv6: " + data.mv6[intCount];
            strTBLm = strTBLm + "IPv6: " + data.mv6[intCount];
            strTBLm = geoIPImageIPv6(data.mv6[intCount], li, strTBLm);
        }

        // URL
        lilink = document.createElement('li');
        aLink = document.createElement('a');

        strHost = "http://m." + data.strDomain;
        aLink.href = strHost;
        aLink.addEventListener('click',
            function (event) {
                event.preventDefault();
                window.open(this.href);
            },
        false);

        aLink.innerText = "link (be careful) m." + data.strDomain;
        lilink.appendChild(aLink);
        ul.appendChild(lilink);
    }

    // webmail IPv4 Address
    var strTBLwebmail = "";
    if (data.webmailv4.length > 0) {
        ul = document.createElement('ul');
        domDiv.appendChild(ul);

        for (intCount = 0; intCount < data.webmailv4.length; intCount++) {
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "webmail IPv4: " + data.webmailv4[intCount];
            strTBLwebmail = strTBLwebmail + "IPv4: " + data.webmailv4[intCount];
            strTBLwebmail = geoIPImageIPv4(data.webmailv4[intCount], li, strTBLwebmail);
        }

        // URL
        lilink = document.createElement('li');
        aLink = document.createElement('a');

        strHost = "http://webmail." + data.strDomain;
        aLink.href = strHost;
        aLink.addEventListener('click',
            function (event) {
                event.preventDefault();
                window.open(this.href);
            },
        false);

        aLink.innerText = "link (be careful) webmail." + data.strDomain;
        lilink.appendChild(aLink);
        ul.appendChild(lilink);
    }

    // webmail IPv6 Address
    if (data.webmailv6.length > 0) {
        ul = document.createElement('ul');
        domDiv.appendChild(ul);

        for (intCount = 0; intCount < data.webmailv6.length; intCount++) {
            li = document.createElement('li');
            ul.appendChild(li);
            li.innerText = "webmail IPv6: " + data.webmailv6[intCount];
            strTBLwebmail = strTBLwebmail + "IPv6: " + data.webmailv6[intCount];
            strTBLwebmail = geoIPImageIPv6(data.webmailv6[intCount], li, strTBLwebmail);
        }

        // URL
        lilink = document.createElement('li');
        aLink = document.createElement('a');
        
        strHost = "http://webmail." + data.strDomain;
        aLink.href = strHost;
        aLink.addEventListener('click',
            function (event) {
                event.preventDefault();
                window.open(this.href);
            },
        false);

        aLink.innerText = "link (be careful) webmail." + data.strDomain;
        lilink.appendChild(aLink);
        ul.appendChild(lilink);
    }



    var strDomain = "";

    if (document.getElementById("host").value == data.strDomain) {
        strDomain = data.strDomain + " (original)";
    } else {
        strDomain = data.strDomain;
    }

    // Add the results row to the table
    $('#resultstabletable').dataTable().fnAddData(
                                                [
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

// -------------------------------------
// this is called for each domain
// to parse the JSON results
// -------------------------------------
function loadDetails(strDomain, mynoresdiv) {
    var URL = "./entity.ncc";
    var strTag = " ( ";
    var intCount = 0;

    $.post(URL, { host: strDomain }, function (data) {
            //console.log(data)

            // Header
            var node = document.createElement("H3");
            node.setAttribute("id", data.strDomain);


            var strTag = generateTag(data);
            if (strTag != null) {

                // Results header value
                var textnode = document.createTextNode(data.strDomain + " " + strTag);
                node.appendChild(textnode);
                document.getElementById("results").appendChild(node);

                // Results div
                var mydiv = document.createElement("div");
                fillDetails(mydiv, data);
                document.getElementById("results").appendChild(mydiv);

            } else {
                // Don't both creating those with nothing interesting
                // var textnode = document.createTextNode(data.strDomain);
            }

            intPBarCount++
            // Style
            if (intPBarCount >= intPBarMax) {

                /*
                 * Insert a 'details' header to the table
                 */
                var nCloneTh = document.createElement( 'th' );
                $('#resultstabletable thead tr').each( function () {
                    this.insertBefore( nCloneTh, this.childNodes[0] );
                } );

                /*
                 * Insert a 'details' column & button to the table
                 */
                var nCloneTd = document.createElement( 'td' );
                nCloneTd.innerHTML = '<img src="images/add.png">';
                nCloneTd.className = "center";

                $('#resultstabletable tbody tr').each( function () {
                    this.insertBefore(  nCloneTd.cloneNode( true ), this.childNodes[0] );
                } );

                /* Add event listener for opening and closing details
                 * Note that the indicator for showing which row is open is not controlled by DataTables,
                 * rather it is done here
                 */
                $('#resultstabletable tbody td img').on('click', function () {
                    var nTr = $(this).parents('tr')[0];
                    if ( oTable.fnIsOpen(nTr) )
                    {
                        /* This row is already open - close it */
                        this.src = "images/add.png";
                        oTable.fnClose( nTr );
                    }
                    else
                    {
                        /* Open this row */
                        this.src = "images/minus.png";
                        oTable.fnOpen( nTr, fnFormatDetails(oTable, nTr), 'details' );
                        /* Ensure that the new row is as wide as the table is now that it has the extra details column */
                        newrow = $(this).closest("tr").next("tr").children("td");
                        newrow.attr("colspan", parseInt(newrow.attr("colspan")) + 1);
                    }
                } );

                // Fill the no results div
                fillNoResDetails(mynoresdiv);
                $("#results").accordion("refresh");
                // Hide the progress bar
                document.getElementById("progressbar").style.display = "none";
                // Shows the results
                // document.getElementById("results").style.display = "block";
                // Shows the original form
                document.getElementById("typogulator").style.display = "block";
                // Shows the results table
                document.getElementById("resultstable").style.display = "block";
            }

            $("#progressbar").progressbar("option", "value", intPBarCount);

            //$("#results").accordion("refresh");
        })
        .fail(function (xhr, textStatus, errorThrown) {
    
        })
        .always(function (data) {
    
        }, 'json');
}


/* Formating function for row details */
function fnFormatDetails ( oTable, nTr )
{
    var aData = oTable.fnGetData( nTr );
    var strDomain = aData[0];
    if (strDomain.indexOf(" ") > -1)
    {
        strDomain = strDomain.substr(0, strDomain.indexOf(" "));
    }

    // var sOut = '';
    var domOut = document.createDocumentFragment();

    //Links
    if (aData[3] != "" || aData[4] != "" || aData[5] != "")
    {
        // sOut += '<h5>Links (be careful!):</h5>';
        var domH5 = document.createElement('h5');
        domH5.innerText = "Links (be careful!)";
        domOut.appendChild(domH5);

        // sOut += '<table cellpadding="5" cellspacing="0" border="0">';
        var domTBL = document.createElement("table");
        domTBL.setAttribute('cellpadding', 5);
        domTBL.setAttribute('cellspacing', 0);
        domTBL.setAttribute('border', 0);

        
        if (aData[3] != "")
        {
            var domTR = document.createElement('tr');
            domTBL.appendChild(domTR);

            var domTD = document.createElement('td');
            domTR.appendChild(domTD);

            aLink = document.createElement('a');
            strHost = "http://www." + strDomain;
            aLink.href = strHost;
            aLink.addEventListener('click',
                function (event) {
                    event.preventDefault();
                    window.open(this.href);
                },
            false);
            aLink.innerText = "www." + strDomain;

            domTD.appendChild(aLink);

            
        }
        if (aData[4] != "")
        {
            var domTR = document.createElement('tr');
            domTBL.appendChild(domTR);

            var domTD = document.createElement('td');
            domTR.appendChild(domTD);

            aLink = document.createElement('a');
            strHost = "http://webmail." + strDomain;
            aLink.href = strHost;
            aLink.addEventListener('click',
                function (event) {
                    event.preventDefault();
                    window.open(this.href);
                },
            false);
            aLink.innerText = "webmail." + strDomain;

            domTD.appendChild(aLink);
        }
        if (aData[5] != "")
        {
            var domTR = document.createElement('tr');
            domTBL.appendChild(domTR);

            var domTD = document.createElement('td');
            domTR.appendChild(domTD);

            aLink = document.createElement('a');
            strHost = "http://m." + strDomain;
            aLink.href = strHost;
            aLink.addEventListener('click',
                function (event) {
                    event.preventDefault();
                    window.open(this.href);
                },
            false);
            aLink.innerText = "m." + strDomain;

            domTD.appendChild(aLink);
        }
        
        // sOut += '</table>';
        domOut.appendChild(domTBL);
    }

    //Whois
    //sOut += '<h5>WHOIS Data:</h5>';
    //sOut += '<pre class="whois"></pre>';
    
    var domH5Whois = document.createElement('h5');
    domH5Whois.innerText = "WHOIS Data:";
    domOut.appendChild(domH5Whois);

    var domPre = document.createElement('pre');
    domPre.setAttribute('class', 'whois');
    domPre.innerText = "Loading...\r\n\r\n";
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
                $("#typoamountdesc").val("Quick");
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

    // init the accordion
    $("#results").accordion();
    $("#results").accordion("option", "heightStyle", "content");

    // init the progressbar
    $("#progressbar").progressbar({
        value: 0
    });

    // init the data table
    oTable = $('#resultstabletable').dataTable({
        'iDisplayLength': 100
    });

    // Hide the progressbar
    document.getElementById("progressbar").style.display = "none";

    //Autofocus the search box
    $("#host").focus();

    $("#typogulator").submit(function () {
        // Hide the form
        document.getElementById("typogulator").style.display = "none";
        // Hide and empty the results
        // document.getElementById("results").style.display = "none";
        emptyresults();
        // Hide the results table
        document.getElementById("resultstable").style.display = "none";
        // Reset and show the progress bar
        intPBarCount = 0;
        $("#progressbar").progressbar("option", "value", 0);
        document.getElementById("progressbar").style.display = "block";
        // Reset the list of domains which didn't yield results 
        domainsNoResults = new Array();
        // Reset the table
        $('#resultstabletable').dataTable()._fnClearTable();

        // Set cookie
        try {
            setCookie("typofinder-domain", document.getElementById('host').value, 365);
        } catch(err){
        
        }
        
        try {
            setCookie("typofinder-typos", document.getElementById('typos').value, 365);
        } catch(err){
        
        }

        try {
            setCookie("typofinder-bitflip", document.getElementById('bitflip').value, 365);
        } catch(err){
        
        }

        try {
            setCookie("typofinder-homoglyph", document.getElementById('homoglyph').value, 365);
        } catch(err){
        
        }

        try {
            setCookie("typofinder-tlds", document.getElementById('tld').value, 365);
        } catch(err){
        
        }

        try {
            setCookie("typofinder-typoamount", document.getElementById('typoamount').value, 365);
        } catch(err){
        
        }

        try {
            setCookie("typofinder-typoamountdesc", document.getElementById('typoamountdesc').value, 365);
        } catch(err){
        
        } 

        //Do the AJAX post
        $.post($("#typogulator").attr("action"), $("#typogulator").serialize(), function (data) {
            //$("#results").html(data);

            // max for the progress bar
            intPBarMax = data.length + 1; // we add one to factor in the first request

            // set the max on the progress bar
            $("#progressbar").progressbar("option", "max", data.length);

            // Create a top entry in the results for domains with no findings
            var node = document.createElement("H3");
            node.setAttribute("id", "NoResults");
            var textnode = document.createTextNode("Typos with no results");
            node.appendChild(textnode);
            document.getElementById("results").appendChild(node);
            var mynoresdiv = document.createElement("div");
            document.getElementById("results").appendChild(mynoresdiv);

            // Get the original domains data
            getMasterData();

            // now loop through and process them
            for (key in data) {
                // the success function
                loadDetails(data[key], mynoresdiv);
            }


        })
            .fail(function (xhr, textStatus, errorThrown) {
                console.log("error " + textStatus)
                document.getElementById("progressbar").style.display = "none";
                // document.getElementById("results").style.display = "none";
                document.getElementById("resultstable").style.display = "none";
                document.getElementById("typogulator").style.display = "block";
            })
            .always(function (data) {
                //console.log(data)
            }, 'json');

        //Important. Stop the normal POST
        return false;
    });
});
