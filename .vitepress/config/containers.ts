import container from 'markdown-it-container'
import type { UserConfig } from 'vitepress'

function createContainer(name: string) {
  return [container, name, {
    render(tokens: any[], idx: number) {
      if (tokens[idx].nesting === 1) {
        return `<div class="custom-block ${name}">\n`
      }
      return '</div>\n'
    }
  }] as const
}

export const markdown: UserConfig['markdown'] = {
  math: true,
  config: (md) => {
    md.use(...createContainer('definition'))
    md.use(...createContainer('theorem'))
    md.use(...createContainer('proof'))
  },
}
