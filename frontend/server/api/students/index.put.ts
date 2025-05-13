export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const query = await getQuery(event)
    const body = await readBody(event)
    if (session.secure){
      const result = await $fetch(`http://127.0.0.1:8000/api/student/${query.student_id_old}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${session.secure.auth_token}`
        },
        body: body,
        query: {
            subjects: query.subjects,
            rfid: query.rfid
        }    
      }
    )
      return result
    }

    return {"error": "failed adding the subjects"}
  })