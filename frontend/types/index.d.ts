export { };

declare global {

    interface Section {
        name: string;
        }

        interface AcademicPeriod {
        semester: string;
        academic_year: string;
        }

        interface SubjectOut {
        subject_id: number;
        subject_name: string;
        schedule: string[];
        start_time: string;
        end_time: string;
        section: Section[];          // an array of sections per subject
        period: AcademicPeriod[];    // an array with typically one period object
        }


    interface Subjects {
        subject_id: number
        subject_name: string
        section: string
        schedule: string[]
        start_time: string,
        end_time: string,
    }
    
    interface Student {
        student_id: number
        first_name: string
        middle_initial: string
        last_name: string
        email: string
        alt_email?: string
        gender: string
        course: string
        face_data: string
    }

    interface StudentQueryResponse {
        items?: Student[]
        count: number
    }

    interface StudentRegisterError {
        error: string;
    }
      
    interface StudentRegisterSuccess {
        success: string;
    }
      
    type StudentRegister = StudentRegisterError | StudentRegisterSuccess;

    interface TimeInOutResponse {
        time_in: string;
        success: boolean;
        message?: string;
        time_out?: string;
        is_present?: string;
        student_name?: string;
    }

    interface SignUpResponse {
        first_name: string
        last_name: string
        email: string
        id: number
        error?: boolean
        message?: string
    }

    interface Teacher {
        id: number
        first_name: string
        last_name: string
        email: string
    }

    interface AttendanceRecord {
        attendance_info_id: number
        is_present: boolean
        time_in: string | null
        time_out: string | null
        sheet_id: number
        student_id: number
        student_name: string
        subject_name: string
        session_date: string
    }

    interface QueryError {
        success: boolean
        message?: string
    }

    interface TimeSlot {
        start: string
        end: string
    }
    
    interface DayData {
        day_of_week: string
        free_slots: TimeSlot[]
    }

    interface DayScheduleProps {
        day: DayData
    }

    interface Stats {
        totalSessions: number
        presentCount: number
        absentCount: number
        averageAttendance: number
    }
}