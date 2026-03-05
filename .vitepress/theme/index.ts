import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import CustomHero from './CustomHero.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'home-hero-info': () => h(CustomHero),
    })
  },
}
