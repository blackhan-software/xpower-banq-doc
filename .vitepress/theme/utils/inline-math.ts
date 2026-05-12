export function inlineMath(text: string): string {
  return text
    .replace(/\$\$([\s\S]+?)\$\$/g, '$$$1$$')
    .replace(/\\\[([\s\S]+?)\\\]/g, '$$$1$$')
}
