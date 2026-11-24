// The answer sheet's writer, in JavaScript (W2-211 PG-3; the spec's "The answer sheet").
// It is the same text, byte for byte, as `gov.decisions.sheet.write_sheet`; the decisions page embeds it.
// Run alone: `node decisions-sheet.js`, JSON on standard input
//   {batch, hash, answered, picks: [[id, letter or "skip", note or null], ...]}
// and the sheet on standard output.
(function (root) {
  "use strict";
  // every character Python's str.splitlines and JavaScript treat as a line break
  var BREAKS = /\r\n|[\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029]/g;

  function writeSheet(batch, hash, answered, picks) {
    var lines = ["GOV-ANSWERS 1", "batch: " + batch, "hash: " + hash, "answered: " + answered,
                 "count: " + picks.length];
    picks.forEach(function (pick) {
      var line = pick[0] + ": " + pick[1];
      if (pick[2]) { line += " | note: " + String(pick[2]).replace(BREAKS, " "); }
      lines.push(line);
    });
    lines.push("END");
    return lines.join("\n") + "\n";
  }

  if (typeof module !== "undefined" && module.exports) { module.exports = { writeSheet: writeSheet }; }
  root.writeSheet = writeSheet;

  if (typeof require !== "undefined" && typeof module !== "undefined" && require.main === module) {
    var chunks = [];
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", function (c) { chunks.push(c); });
    process.stdin.on("end", function () {
      var d = JSON.parse(chunks.join(""));
      process.stdout.write(writeSheet(d.batch, d.hash, d.answered, d.picks));
    });
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
