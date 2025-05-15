
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const body = await readBody(event)

    if(!session.secure){
        return sendRedirect(event, '/login')
    }

    await $fetch<Teacher>("http://127.0.0.1:8000/auth/users/set_password/", {
        method: "POST",
        headers: {
        "Authorization": `Token ${session.secure.auth_token}`
        },
        body: body
    }).catch((err) => {
        return err
    })
    .then((res) => {
        console.log(res)
        return res
    })
})
  