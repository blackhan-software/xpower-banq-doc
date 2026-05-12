let mathReady: Promise<void> | null = null

export function loadMathJax(): Promise<void> {
  if (mathReady) {
    return mathReady
  }
  if (typeof window === 'undefined') {
    return Promise.resolve()
  }
  mathReady = new Promise<void>((resolve, reject) => {
    const w = window as any
    if (w.MathJax?.typesetPromise) {
      return resolve()
    }
    w.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
      },
      svg: { fontCache: 'global' },
      startup: {
        ready() {
          w.MathJax.startup.defaultReady()
          resolve()
        },
      },
    }
    const s = document.createElement('script')
    s.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'
    s.async = true
    s.onerror = () => reject(new Error('MathJax failed to load'))
    document.head.appendChild(s)
  })
  return mathReady
}

export async function typesetMath(el: HTMLElement | null): Promise<void> {
  if (el) try {
    await loadMathJax()
    const mj = (window as any).MathJax
    if (mj?.typesetPromise) await mj.typesetPromise([el])
  } catch { }
}
