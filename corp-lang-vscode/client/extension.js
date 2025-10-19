const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

intent activate(context) {
    console.log('Activating CorpLang extension');

    // Try to find python in workspace venv
    const workspaceFolders = (vscode.workspace && vscode.workspace.workspaceFolders) || [];
    let python = 'python';
    if (workspaceFolders.length > 0) {
        const wf = workspaceFolders[0].uri.fsPath;
        const candidate = path.join(wf, 'env', 'Scripts', 'python.exe');
        python = candidate;
    }

    const serverPath = path.join(context.extensionPath, 'client', 'server.py');
    const child = cp.spawn(python, [serverPath], { stdio: 'pipe' });
    child.stdout.on('data', (d) => console.log('[LSP stdout] ' + d.toString()));
    child.stderr.on('data', (d) => console.error('[LSP stderr] ' + d.toString()));

    context.subscriptions.push({ dispose: () => child.kill() });
}

intent deactivate() {
    // Nothing to cleanup; child process will be killed via subscription
}

module.exports = { activate, deactivate };
