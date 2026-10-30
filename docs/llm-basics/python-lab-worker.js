/* Module Worker：真实 Python 在此运行，页面可随时终止整个 Worker。 */
let engine;
async function initialize(harnessURL) {
  if (!engine) engine = (async () => {
    const base = new URL('./vendor/pyodide/314.0.7/', import.meta.url).href;
    const [{loadPyodide}, response] = await Promise.all([
      import(base + 'pyodide.mjs'), fetch(harnessURL, {cache:'no-store'})
    ]);
    if (!response.ok) throw new Error('无法加载实验检查器（HTTP '+response.status+'）。');
    const harness = await response.text();
    const python = await loadPyodide({indexURL:base});
    await python.runPythonAsync(harness);
    return python;
  })();
  return engine;
}
self.onmessage = async ({data}) => {
  try {
    if (data.type === 'init') {
      await initialize(data.harnessURL);
      self.postMessage({type:'ready', id:data.id});
    } else if (data.type === 'run') {
      const python = await engine;
      if (!python) throw new Error('Python 尚未初始化。');
      self.postMessage({type:'executing', id:data.id});
      const run = python.globals.get('run_lab');
      try {
        const payload = JSON.parse(run(data.code, data.scenario, data.mode));
        self.postMessage({type:'result', id:data.id, payload});
      } finally { run.destroy(); }
    }
  } catch (error) {
    self.postMessage({type:'error', id:data.id, error:String(error?.message||error).slice(0,5000)});
  }
};
