import { format } from "date-fns"

export default function (
    records: AttendanceRecord[],
    filename = `attendance_report_${format(new Date(), "yyyy-MM-dd")}`
  ) {
    // 1. Build the header row
    const headers = [
      'Student',
      'Subject',
      'Date',
      'Status',
      'Time In',
      'Time Out'
    ]
    // 2. Map each record into a CSV row, escaping commas if needed
    const rows = records.map(r => [
      r.student_name,
      r.subject_name,
      r.session_date,
      r.is_present ? 'Present' : 'No Time Out',
      r.time_in || '-',
      r.time_out || '-'
    ].map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    // 3. Combine header + rows into one CSV string
    const csvContent = [headers.join(','), ...rows].join('\r\n')
    // 4. Create a Blob and object URL (more efficient than data URI for large files)
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)  // createObjectURL preferred over encodeURI for large data :contentReference[oaicite:0]{index=0}
    // 5. Create & click hidden link to download
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', filename)  // sets the downloaded file name :contentReference[oaicite:1]{index=1}
    document.body.appendChild(link)          // Firefox requires link to be in the DOM :contentReference[oaicite:2]{index=2}
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }