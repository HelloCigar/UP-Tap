import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { format } from "date-fns"

export default function (
  records: AttendanceRecord[],
  startDate: Date,
  endDate: Date
) {
  // 1. Initialize jsPDF
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  
  // 2. Title
  doc.setFontSize(18)
  doc.text('UP Attendance Report', 40, 50)
  
  // 3. Date Range
  doc.setFontSize(11)
  doc.text(
    `From: ${startDate.toLocaleDateString()}  To: ${endDate.toLocaleDateString()}`,
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

  // 5. Draw table
  autoTable(doc, {
    head,
    body,
    startY: 90,
    theme: 'striped',
    headStyles: { 
      fillColor: [252, 0, 0] 
    },
    bodyStyles: { 
      lineColor: [252, 0, 0] 
    },
    styles: { fontSize: 10 },
    margin: { left: 40, right: 40 }
  })

  // 6. Save PDF
  doc.save(`attendance_report_${format(new Date(), "yyyy-MM-dd")}.pdf`)
}