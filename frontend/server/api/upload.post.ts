export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const result = await $fetch(`http://127.0.0.1:8000/api/upload`, {
          method: "POST",
          body: body,
        }
    )
    
    return result
  })
  