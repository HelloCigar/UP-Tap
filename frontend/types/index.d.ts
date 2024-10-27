export { };

declare global {
    interface Subjects {
        subject_id: number
        subject_name: string
        section: string
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
    }
}