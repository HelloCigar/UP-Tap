export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const body = await readBody(event)
    if (session.secure){
      await $fetch("http://127.0.0.1:8000/api/teachers/subjects", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${session.secure.auth_token}`
        },
        body: body    
      }
    )
    .then((res) => {
        return res
    })
    }
})