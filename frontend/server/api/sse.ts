export default defineEventHandler(async (event) => {
  const response = await fetch('http://127.0.0.1:8000/events', {
    method: 'GET',
    headers: {
      'Accept': 'text/event-stream',
    }
  });

  if (!response.body) {
    throw new Error('No response body from server.');
  }

  // Set the appropriate headers
  event.node.res.setHeader('Content-Type', 'text/event-stream');
  event.node.res.setHeader('Cache-Control', 'no-cache');
  event.node.res.setHeader('Connection', 'keep-alive');

  // Pipe the readable stream directly to the response
  response.body.pipeTo(new WritableStream({
    write(chunk) {
      event.node.res.write(chunk);
    },
    close() {
      event.node.res.end();
    },
    abort(err) {
      console.error('Stream aborted:', err);
      event.node.res.end();
    }
  }));
});
