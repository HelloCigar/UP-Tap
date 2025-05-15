
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)

    if(!session.secure){
        return sendRedirect(event, '/login')
    }

    const { first_name, last_name } = await readBody(event)

    // Build payload with conditional properties
    const payload = {
        // only add first_name if non-empty
        ...(first_name !== "" && { first_name }),
        // only add last_name if non-empty
        ...(last_name  !== "" && { last_name  }),
    }

    await $fetch<Teacher>("http://127.0.0.1:8000/auth/users/me/", {
        method: "PATCH",
        headers: {
        "Authorization": `Token ${session.secure.auth_token}`
        },
        body: payload
    })
    .then((res) => {
        return res
    })
})
  