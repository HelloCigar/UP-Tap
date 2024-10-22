// auth.d.ts
declare module '#auth-utils' {
  interface User {
    // Add your own fields
    auth_token: string
  }

  interface UserSession {
    // Add your own fields
  }

  interface SecureSessionData {
    // Add your own fields
    auth_token: string
  }
}

export {}