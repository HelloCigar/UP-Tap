export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    if (!session.secure) return sendRedirect(event, '/login')
  
    const form = await readMultipartFormData(event)
    const query = getQuery(event)
  
    if (!form || !form.length) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file uploaded',
      })
    }
  
    const filePart = form[0] // just get first if unnamed
    if (!filePart || !filePart.data || !filePart.filename) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Invalid file format',
      })
    }
  
    // Convert file part to a FormData-compatible File
    const file = new File([filePart.data as Buffer], filePart.filename, {
      type: filePart.type || 'text/csv',
    })
  
    // Build FormData
    const formData = new FormData()
    formData.set('file', file)
  
    const subject_id = query.subject_id?.toString() || ''
  
    // Send request using native `fetch` (undici)
    const response = await $fetch(`http://127.0.0.1:8000/api/teachers/upload-classlist`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${session.secure.auth_token}`,
      },
      query: query,
      body: formData,
    })

    return response
  })