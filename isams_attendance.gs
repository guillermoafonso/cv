// =============================================================================
// iSams Registration Attendance Extraction - Google Apps Script
// =============================================================================
// Extracts AM/PM registration attendance marks from iSams REST API
// and writes them to the active Google Sheet.
//
// Setup:
// 1. Replace the placeholder credentials below with your school's values
// 2. Copy this file into your Google Sheet's Apps Script editor
//    (Extensions > Apps Script)
// 3. Run fetchRegistrationAttendance() from the script editor or set a trigger
// =============================================================================

// ---- Credentials (replace with your school's values) ----
var SCHOOL_ID     = "YOUR_CLIENT_ID_HERE";
var SCHOOL_CODE   = "YOUR_CLIENT_SECRET_HERE";
var SCHOOL_URL    = "https://YOUR_SCHOOL.isams.cloud/auth/connect/token";
var API_BASE_URL  = "https://YOUR_SCHOOL.isams.cloud/api";

// ---- Configuration ----
var SHEET_NAME    = "Attendance";       // Name of the sheet to write to
var DATE_FORMAT   = "yyyy-MM-dd";       // Date format for API queries

/**
 * Authenticates with iSams and returns request options with bearer token.
 * Based on existing urlTokenExtraction pattern.
 */
function getAuthOptions() {
  var payload = {
    "client_id"    : SCHOOL_ID,
    "client_secret": SCHOOL_CODE,
    "grant_type"   : "client_credentials",
    "scope"        : "restapi"
  };

  var options = {
    "method"     : "POST",
    "Accept"     : "application/json",
    "contentType": "application/x-www-form-urlencoded",
    "payload"    : payload,
    "muteHttpExceptions": true
  };

  var response   = UrlFetchApp.fetch(SCHOOL_URL, options);
  var statusCode = response.getResponseCode();

  if (statusCode !== 200) {
    throw new Error("Authentication failed (HTTP " + statusCode + "): " + response.getContentText());
  }

  var dataAll     = JSON.parse(response.getContentText());
  var tokenAccess = dataAll.access_token;
  var tokenType   = dataAll.token_type;

  return {
    "method"  : "GET",
    "Accept"  : "application/json",
    "headers" : { "Authorization": tokenType + " " + tokenAccess },
    "muteHttpExceptions": true
  };
}

/**
 * Fetches a paginated API endpoint, collecting all results.
 * iSams REST API uses page/pageSize query parameters.
 */
function fetchAllPages(endpoint, authOptions) {
  var page     = 1;
  var pageSize = 100;
  var allItems = [];

  while (true) {
    var separator = endpoint.indexOf("?") === -1 ? "?" : "&";
    var url = API_BASE_URL + endpoint + separator + "page=" + page + "&pageSize=" + pageSize;

    var response   = UrlFetchApp.fetch(url, authOptions);
    var statusCode = response.getResponseCode();

    if (statusCode !== 200) {
      throw new Error("API request failed (HTTP " + statusCode + "): " + url + "\n" + response.getContentText());
    }

    var data  = JSON.parse(response.getContentText());
    var items = data.sets || data.items || data;

    if (!Array.isArray(items) || items.length === 0) {
      break;
    }

    allItems = allItems.concat(items);

    if (items.length < pageSize) {
      break;
    }

    page++;
  }

  return allItems;
}

/**
 * Fetches a single API endpoint (no pagination).
 */
function fetchEndpoint(endpoint, authOptions) {
  var url = API_BASE_URL + endpoint;

  var response   = UrlFetchApp.fetch(url, authOptions);
  var statusCode = response.getResponseCode();

  if (statusCode !== 200) {
    throw new Error("API request failed (HTTP " + statusCode + "): " + url + "\n" + response.getContentText());
  }

  return JSON.parse(response.getContentText());
}

/**
 * Main function: fetches registration attendance marks and writes to sheet.
 * Pulls today's registration marks by default; pass a date string to override.
 */
function fetchRegistrationAttendance(dateStr) {
  var date = dateStr || Utilities.formatDate(new Date(), Session.getScriptTimeZone(), DATE_FORMAT);

  Logger.log("Fetching registration attendance for: " + date);

  var authOptions = getAuthOptions();

  // Fetch registration attendance for the given date
  var endpoint = "/registration/attendance?date=" + date;
  var records  = fetchAllPages(endpoint, authOptions);

  Logger.log("Fetched " + records.length + " attendance records");

  if (records.length === 0) {
    SpreadsheetApp.getUi().alert("No attendance records found for " + date);
    return;
  }

  writeAttendanceToSheet(records, date);
}

/**
 * Fetches registration attendance for a date range.
 * Useful for bulk extraction (e.g. a term's data).
 */
function fetchAttendanceRange(startDate, endDate) {
  var authOptions = getAuthOptions();
  var endpoint    = "/registration/attendance?startDate=" + startDate + "&endDate=" + endDate;
  var records     = fetchAllPages(endpoint, authOptions);

  Logger.log("Fetched " + records.length + " records for " + startDate + " to " + endDate);

  if (records.length === 0) {
    SpreadsheetApp.getUi().alert("No attendance records found for " + startDate + " to " + endDate);
    return;
  }

  writeAttendanceToSheet(records, startDate + " to " + endDate);
}

/**
 * Writes attendance records to the configured sheet.
 */
function writeAttendanceToSheet(records, label) {
  var ss    = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }

  // Build header row from the first record's keys
  var headers = Object.keys(records[0]);

  // Build data rows
  var rows = records.map(function(record) {
    return headers.map(function(key) {
      var val = record[key];
      if (val === null || val === undefined) return "";
      if (typeof val === "object") return JSON.stringify(val);
      return val;
    });
  });

  // Clear existing content and write
  sheet.clear();
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight("bold");
  sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);

  // Auto-resize columns
  for (var i = 1; i <= headers.length; i++) {
    sheet.autoResizeColumn(i);
  }

  Logger.log("Wrote " + rows.length + " rows to '" + SHEET_NAME + "' sheet (" + label + ")");
}

/**
 * Adds a custom menu to the Google Sheet for easy access.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("iSams Attendance")
    .addItem("Fetch Today's Attendance", "fetchRegistrationAttendance")
    .addItem("Fetch Date Range...", "showDateRangeDialog")
    .addToUi();
}

/**
 * Shows a dialog for entering a date range.
 */
function showDateRangeDialog() {
  var html = HtmlService.createHtmlOutput(
    '<form onsubmit="google.script.run.withSuccessHandler(function(){google.script.host.close()}).fetchAttendanceRange(document.getElementById(\'start\').value,document.getElementById(\'end\').value);return false">' +
    '<label>Start Date: <input type="date" id="start" required></label><br><br>' +
    '<label>End Date: <input type="date" id="end" required></label><br><br>' +
    '<input type="submit" value="Fetch">' +
    '</form>'
  ).setWidth(300).setHeight(150);

  SpreadsheetApp.getUi().showModalDialog(html, "Fetch Attendance Range");
}
