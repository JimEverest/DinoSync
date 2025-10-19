# 创建笔记，含标题，tag

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/openapi/createNote:
    post:
      summary: 创建笔记，含标题，tag
      deprecated: false
      description: 创建笔记
      tags: []
      parameters:
        - name: Authorization
          in: header
          description: api token
          required: false
          example: api token
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                  description: 标题
                content:
                  type: string
                  description: 正文
                tags:
                  type: array
                  items:
                    type: string
                  description: 标签
              x-apifox-orders:
                - title
                - content
                - tags
              required:
                - title
                - content
                - tags
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                type: object
                properties: {}
          headers: {}
          x-apifox-name: OK
      security: []
      x-apifox-folder: ''
      x-apifox-status: developing
      x-run-in-apifox: https://app.apifox.com/web/project/3603287/apis/api-320755687-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```