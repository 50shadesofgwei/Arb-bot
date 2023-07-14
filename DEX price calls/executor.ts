import express from 'express';
import { spawn } from 'child_process';

const args = process.argv.slice(2); // get command-line arguments
const token_address = args[0];
const functionName = args[1];

const app = express();
const port = 3000;

app.get('/main', async (req, res) => {
    const token_address = req.query.token_address;
    if (typeof token_address === 'string') {
      const child = spawn('ts-node', ['index.ts', token_address]);

          // Log output and errors
      child.stdout.on('data', (data) => console.log(`stdout: ${data}`));
      child.stderr.on('data', (data) => console.error(`stderr: ${data}`));

      // Log when script is done
      child.on('close', (code) => console.log(`child process exited with code ${code}`));

      // Acknowledge the request
      res.status(200).send('Function execution started in a new instance of the script.');
    } else {
      res.status(400).send('Bad Request: token_address is required');
    }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});