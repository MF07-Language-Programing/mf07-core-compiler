const cp = require('child_process');
const path = require('path');

function startServer(context) {
    // Try to use workspace virtualenv python if available, else default 'python'
    const workspaceFolders = (vscode.workspace && vscode.workspace.workspaceFolders) || [];
    let python = 'python';
    if (workspaceFolders.length > 0) {
        const wf = workspaceFolders[0].uri.fsPath;
        const candidate = path.join(wf, 'env', 'Scripts', 'python.exe');
        // Note: existence check is not available here; Node child process will fail if not found
        python = candidate;
    }

    const serverPath = path.join(context.extensionPath, 'client', 'server.py');
    const child = cp.spawn(python, [serverPath], { stdio: 'pipe' });
    child.stdout.on('data', (d) => console.log('[LSP stdout] ' + d.toString()));
    child.stderr.on('data', (d) => console.error('[LSP stderr] ' + d.toString()));
    return child;
}

module.exports = { startServer };
