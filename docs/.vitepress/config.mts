import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Notify Bridge",
  description: "A flexible notification bridge for sending messages to various platforms",
  base: '/notify-bridge/',
  
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
  ],

  locales: {
    root: {
      label: 'English',
      lang: 'en',
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      themeConfig: {
        nav: [
          { text: '首页', link: '/zh/' },
          { text: '指南', link: '/zh/guide/getting-started' },
          { text: 'API', link: '/zh/api/core' },
        ],
        sidebar: {
          '/zh/guide/': [
            {
              text: '入门',
              items: [
                { text: '快速开始', link: '/zh/guide/getting-started' },
                { text: '安装', link: '/zh/guide/installation' },
              ]
            },
            {
              text: '平台',
              items: [
                { text: '企业微信 (WeCom)', link: '/zh/guide/wecom' },
                { text: '飞书 (Feishu)', link: '/zh/guide/feishu' },
                { text: 'GitHub', link: '/zh/guide/github' },
              ]
            },
            {
              text: '高级',
              items: [
                { text: '创建插件', link: '/zh/guide/plugins' },
                { text: '错误处理', link: '/zh/guide/error-handling' },
              ]
            }
          ],
          '/zh/api/': [
            {
              text: 'API 参考',
              items: [
                { text: '核心 API', link: '/zh/api/core' },
                { text: 'Schema', link: '/zh/api/schema' },
                { text: '异常', link: '/zh/api/exceptions' },
              ]
            }
          ]
        }
      }
    }
  },

  themeConfig: {
    logo: '/logo.svg',
    
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'API', link: '/api/core' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Introduction',
          items: [
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: 'Installation', link: '/guide/installation' },
          ]
        },
        {
          text: 'Platforms',
          items: [
            { text: 'WeCom', link: '/guide/wecom' },
            { text: 'Feishu', link: '/guide/feishu' },
            { text: 'GitHub', link: '/guide/github' },
          ]
        },
        {
          text: 'Advanced',
          items: [
            { text: 'Creating Plugins', link: '/guide/plugins' },
            { text: 'Error Handling', link: '/guide/error-handling' },
          ]
        }
      ],
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'Core API', link: '/api/core' },
            { text: 'Schema', link: '/api/schema' },
            { text: 'Exceptions', link: '/api/exceptions' },
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/loonghao/notify-bridge' }
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024-present Long Hao'
    },

    search: {
      provider: 'local'
    },

    editLink: {
      pattern: 'https://github.com/loonghao/notify-bridge/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    }
  }
})
