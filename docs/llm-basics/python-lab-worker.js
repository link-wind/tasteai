/* Module Worker：真实 Python 在此运行，页面可随时终止整个 Worker。 */
let engine;
async function initialize(harnessURL, exercise, configURL) {
  if (!engine) engine = (async () => {
    const base = new URL('./vendor/pyodide/314.0.7/', import.meta.url).href;
    const [{loadPyodide}, response] = await Promise.all([
      import(base + 'pyodide.mjs'), fetch(harnessURL, {cache:'no-store'})
    ]);
    if (!response.ok) throw new Error('无法加载实验检查器（HTTP '+response.status+'）。');
    const harness = await response.text();
    const python = await loadPyodide({indexURL:base});
    if(exercise){
      const configResponse=await fetch(configURL,{cache:'no-store'});
      if(!configResponse.ok)throw new Error('题目数据加载失败。');
      const helper=await fetch(new URL('./core/tasteai_math.py',configURL));
      if(!helper.ok)throw new Error('矩阵工具加载失败。');
      python.globals.set('MATH_SOURCE',await helper.text());
      python.globals.set('LAB_ID',exercise);
      python.globals.set('EXERCISE_JSON',await configResponse.text());
    }
    await python.runPythonAsync(harness);
    return python;
  })();
  return engine;
}
self.onmessage = async ({data}) => {
  try {
    if (data.type === 'init') {
      await initialize(data.harnessURL, data.exercise, data.configURL);
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
