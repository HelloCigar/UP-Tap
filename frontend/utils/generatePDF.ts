import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { format } from 'date-fns'

export default function (
  records: AttendanceRecord[],
  startDate: Date,
  endDate: Date
) {
  // 1. Initialize jsPDF (A4 portrait)
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()

  // 2. Title (18pt) – split into two pieces so we can color “UPTap” red
  const redText = 'UP'
  const blackText = 'Tap Attendance Report'
  doc.setFontSize(18)

  // measure widths
  const redWidth = doc.getTextWidth(redText)
  const blackWidth = doc.getTextWidth(blackText)
  const totalWidth = redWidth + blackWidth

  // compute starting x to center both together
  const xStart = (pageWidth - totalWidth) / 2
  const yTitle = 50

  // draw “UPTap” in red
  doc.setTextColor(252, 0, 0)       // red
  doc.text(redText, xStart, yTitle)

  // draw “ Attendance Report” in black immediately after
  doc.setTextColor(0, 0, 0)         // black
  doc.text(blackText, xStart + redWidth, yTitle)

  // 3. Date Range (11pt)
  doc.setFontSize(11)
  doc.setTextColor(0, 0, 0)
  doc.text(
    `From: ${format(startDate, 'yyyy-MM-dd')}  To: ${format(endDate, 'yyyy-MM-dd')}`,
    40,
    70
  )

  // 4. Prepare table headers and body
  const head = [
    ['Student', 'Subject', 'Date', 'Status', 'Time In', 'Time Out']
  ]
  const body = records.map(r => [
    r.student_name,
    r.subject_name,
    r.session_date,
    r.is_present ? 'Present' : 'No Time Out',
    r.time_in || '-',
    r.time_out || '-'
  ])

  // 5. Draw table (striped theme, red lines)
  autoTable(doc, {
    head,
    body,
    startY: 90,
    theme: 'striped',
    headStyles: {
      fillColor: [252, 0, 0]      // red header background
    },
    bodyStyles: {
      lineColor: [252, 0, 0]      // red row borders
    },
    styles: { fontSize: 10 },
    margin: { left: 40, right: 40 }
  })

  // 6. Save PDF with today’s date
  doc.save(`attendance_report_${format(new Date(), 'yyyy-MM-dd')}.pdf`)
}
