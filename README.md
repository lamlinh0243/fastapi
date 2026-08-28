# FastAPI Homework - Todo API

Mini FastAPI project được xây dựng nhằm thực hành và tổng hợp các kiến thức cơ bản về FastAPI, SQLite, Dependency Injection, CRUD API, CORS, lifespan và Pydantic validation.

## 1. Giới thiệu

Project xây dựng một Todo API đơn giản bằng Python và FastAPI.

API hỗ trợ các chức năng:

- Tạo Todo
- Lấy danh sách Todo
- Lấy thông tin chi tiết một Todo
- Cập nhật Todo
- Xóa Todo
- Kiểm tra trạng thái sống của application
- Kiểm tra trạng thái sẵn sàng của database

Project sử dụng SQLite làm database và `uv` để quản lý environment/package.

## 2. Công nghệ sử dụng

- Python
- FastAPI
- Uvicorn
- SQLite
- Pydantic
- uv
- curl
- Git / GitHub

## 3. Cấu trúc project

```text
fastapi-homework/
├── main.py
├── curl.sh
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
└── src/
```

Các file chính:

| File | Mô tả |
|------|------|
| `main.py` | FastAPI application, database, models và CRUD API |
| `curl.sh` | Script kiểm tra các API endpoint |
| `pyproject.toml` | Khai báo project và dependencies |
| `uv.lock` | Lock phiên bản dependencies |
| `.gitignore` | Các file/thư mục không đưa lên Git |
| `README.md` | Tài liệu hướng dẫn project |

## 4. Data Model

Todo gồm các thuộc tính:

| Field | Type | Mô tả |
|------|------|------|
| `id` | integer | ID tự động tăng |
| `title` | string | Tiêu đề Todo |
| `description` | string/null | Mô tả |
| `completed` | boolean | Trạng thái hoàn thành |
| `priority` | integer | Độ ưu tiên từ 1 đến 5 |

Ví dụ:

```json
{
  "id": 1,
  "title": "Hoc FastAPI",
  "description": "Lam bai tap FastAPI",
  "completed": false,
  "priority": 1
}
```

## 5. FastAPI Endpoints

### Health Check

| Method | Endpoint | Mô tả |
|--------|----------|------|
| GET | `/health/live` | Kiểm tra application đang hoạt động |
| GET | `/health/ready` | Kiểm tra application và database đã sẵn sàng |

### Todo CRUD

| Method | Endpoint | Mô tả |
|--------|----------|------|
| POST | `/todos` | Tạo Todo mới |
| GET | `/todos` | Lấy danh sách Todo |
| GET | `/todos/{todo_id}` | Lấy Todo theo ID |
| PUT | `/todos/{todo_id}` | Cập nhật Todo |
| DELETE | `/todos/{todo_id}` | Xóa Todo |

## 6. Pydantic Validation

Project sử dụng Pydantic để kiểm tra dữ liệu đầu vào.

### Field Validator

`field_validator` được sử dụng để kiểm tra `title`.

Title sẽ được:

- Loại bỏ khoảng trắng đầu/cuối.
- Không được để trống.

### Model Validator

`model_validator` được sử dụng trong model cập nhật Todo.

Khi update, ít nhất một field phải được cung cấp.

Ví dụ không hợp lệ:

```json
{}
```

## 7. Database

Project sử dụng SQLite.

Database được tạo tự động khi application khởi động thông qua `lifespan`.

Database chứa bảng:

```text
todos
```

Các column:

```text
id
title
description
completed
priority
```

File database local không được commit lên Git.

## 8. Dependency Injection

Database connection được cung cấp thông qua FastAPI Dependency Injection:

```python
Depends(get_db)
```

Mỗi request sử dụng database connection và connection được đóng lại sau khi request hoàn thành.

## 9. CORS

Project đã cấu hình CORS middleware để cho phép API nhận request từ các origin khác.

## 10. Lifespan

FastAPI `lifespan` được sử dụng để thực hiện các thao tác khi application:

- Khởi động
- Tắt

Khi application khởi động, database table sẽ được tạo nếu chưa tồn tại.

## 11. Cài đặt môi trường

Project được thiết kế để chạy trên Ubuntu/WSL.

### Clone repository

```bash
git clone <repository-url>
cd fastapi-homework
```

### Cài dependencies

Sử dụng `uv`:

```bash
uv sync
```

## 12. Chạy application

Chạy FastAPI bằng Uvicorn:

```bash
uv run uvicorn main:app --reload
```

Application sẽ chạy tại:

```text
http://127.0.0.1:8000
```

## 13. Swagger API Documentation

Sau khi application chạy, mở:

```text
http://127.0.0.1:8000/docs
```

Swagger UI cho phép xem và test các API endpoint trực tiếp trên trình duyệt.

## 14. Test API bằng curl

Project có file:

```text
curl.sh
```

Cấp quyền thực thi:

```bash
chmod +x curl.sh
```

Sau đó chạy:

```bash
./curl.sh
```

Script kiểm tra:

- Health Live
- Health Ready
- Create Todo
- Get Todo List
- Get Todo Detail
- Update Todo
- Delete Todo

## 15. Ví dụ API

### Create Todo

```bash
curl -X POST "http://127.0.0.1:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hoc FastAPI",
    "description": "Lam bai tap FastAPI",
    "completed": false,
    "priority": 1
  }'
```

### Get Todo List

```bash
curl "http://127.0.0.1:8000/todos"
```

### Get Todo Detail

```bash
curl "http://127.0.0.1:8000/todos/1"
```

### Update Todo

```bash
curl -X PUT "http://127.0.0.1:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true,
    "priority": 3
  }'
```

### Delete Todo

```bash
curl -X DELETE "http://127.0.0.1:8000/todos/1"
```

## 16. Requirements

Project cần đảm bảo chạy được các lệnh:

```bash
uv sync
```

```bash
uv run uvicorn main:app --reload
```

```bash
./curl.sh
```
