export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const result = await $fetch<SignUpResponse>(`http://127.0.0.1:8000/auth/users/activation/`, {
        method: "POST",
        body: body,
        }
    )
    .catch((err) => {
        const errorMessage = err?.data?.detail as string || "An unknown error occurred.";
        return { "error": true, "message": errorMessage };
    });
    if (result) {    
        return result    
    }
})