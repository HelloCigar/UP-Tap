export { };

declare global {

    interface Subjects {
        subject_id: number
        subject_name: string
        time_and_schedule: SubjectTimeAndSchedule[]
    }

    interface SubjectTimeAndSchedule {
        day_of_week: string,
        start_time: string,
        end_time: string,
    }

    interface Student {
        student_id: number
        first_name: string
        last_name: string
        email: string
    }

    interface StudentQueryResponse {
        items: Student[]
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
}