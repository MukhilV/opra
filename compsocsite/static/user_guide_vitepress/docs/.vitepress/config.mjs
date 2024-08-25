import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "OPRA User Guide",
  description: "A VitePress Site",
  base: '/user_docs/', // Set the base URL to '/user_docs/'
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      // { text: 'Examples', link: '/markdown-examples' }
    ],

    sidebar: [
      {
        text: '',
        items: [
          { text: 'Polls', link: '/polls' },
          { text: 'Allocations', link: '/allocations' },
          { text: 'Groups', link: '/groups' }
        ]
      }
    ],

    // socialLinks: [
    //   { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    // ]
  }
})

