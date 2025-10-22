# 根据 id 查询笔记

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/openapi/note/{{笔记 id}}:
    get:
      summary: 根据 id 查询笔记
      deprecated: false
      description: ''
      tags: []
      parameters:
        - name: Authorization
          in: header
          description: ''
          required: false
          example: ''
          schema:
            type: string
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
      x-run-in-apifox: https://app.apifox.com/web/project/3603287/apis/api-361901437-run
components:
  schemas: {}
  securitySchemes: {}
servers: []
security: []

```