import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'

import Hero from './components/hero.vue'
import AskAI from './components/ask-ai/ask-ai.vue'
import Footer from './components/footer.vue'

import 'bootstrap-icons/font/bootstrap-icons.css'
import './styles/index.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'home-hero-info': () => h(Hero),
      'layout-top': () => h(AskAI),
      'layout-bottom': () => h(Footer),
    })
  },
}
