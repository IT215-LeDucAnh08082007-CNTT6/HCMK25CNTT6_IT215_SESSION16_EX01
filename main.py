# PHẦN 1: BÁO CÁO LỖI LOGIC NGHIỆP VỤ (CHỈ RA 4 LỖI LOGIC CHÍNH)
"""
-----------------------------------------------------------------------------------------------------------------------------------------
STT | Lỗi Logic Phát Hiện                   | Kết Quả Thực Tế                 | Kết Quả Mong Đợi               | Nguyên Nhân Gây Lỗi TRONG CODE CŨ
----|---------------------------------------|---------------------------------|--------------------------------|---------------------------------------------------------
1   | Cho phép thêm sinh viên vào           | Trả về 201 Created. Sinh viên   | Phải trả về lỗi 404 Not Found  | Dùng điều kiện `if classroom and ...` nên nếu 
    | lớp học KHÔNG tồn tại trong hệ thống. | được thêm vào với class_id = 99.| và chặn không cho tạo.         | classroom là `None` thì toàn bộ cụm check logic bị bỏ qua.
----|---------------------------------------|---------------------------------|--------------------------------|---------------------------------------------------------
2   | Kiểm tra vượt số lượng tối đa bị      | Trả về 201 Created. Sĩ số lớp   | Phải trả về lỗi 400 Bad Request| Sử dụng toán tử so sánh `>` thay vì `>=`. Lớp có max là 2,
    | sai toán tử, gây tràn sĩ số lớp học.  | tăng lên 3 vượt quá max_students| khi sĩ số hiện tại đã bằng max.| hiện tại đã có 2, khi thêm người thứ 3 thì 2 > 2 là Sai.
----|---------------------------------------|---------------------------------|--------------------------------|---------------------------------------------------------
3   | Kiểm tra trùng mã sinh viên bị sai    | Trả về 201 Created. Cho phép    | Phải trả về lỗi 409 Conflict   | Check trùng mã bị ràng buộc thêm điều kiện cùng lớp: 
    | phạm vi (chỉ check trùng trong 1 lớp).| trùng mã SV001 ở lớp học khác.  | trên TOÀN BỘ hệ thống.         | `and student["class_id"] == student_data.class_id`.
-----------------------------------------------------------------------------------------------------------------------------------------

DỮ LIỆU MINH CHỨNG CHO CÁCH TRACE TEST CASE:
- Test Case Lỗi 1 (Lớp không tồn tại): Gửi JSON {"student_code": "SV003", "full_name": "Test", "class_id": 99} -> Lọt qua và tạo thành công.
- Test Case Lỗi 2 (Lớp đầy): Lớp 1 có max_students = 2, hiện có 2 sinh viên. Gửi JSON {"student_code": "SV003", "full_name": "Test", "class_id": 1} -> Vẫn tạo được sinh viên thứ 3.
- Test Case Lỗi 3 (Trùng mã hệ thống): Gửi JSON {"student_code": "SV001", "full_name": "Test", "class_id": 2} -> Vẫn tạo thành công mã SV001 cho lớp 2.
"""

# PHẦN 2: SOURCE CODE ĐÃ ĐƯỢC VÁ LỖI LOGIC HOÀN CHỈNH

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class StudentCreate(BaseModel):
    student_code: str
    full_name: str
    class_id: int

classrooms = [
    {
        "id": 1,
        "name": "FastAPI Basic",
        "max_students": 2,
        "status": "OPEN"
    },
    {
        "id": 2,
        "name": "Python Foundation",
        "max_students": 3,
        "status": "CLOSED"
    }
]

students = [
    {
        "id": 1,
        "student_code": "SV001",
        "full_name": "Nguyễn Văn An",
        "class_id": 1
    },
    {
        "id": 2,
        "student_code": "SV002",
        "full_name": "Trần Minh Bình",
        "class_id": 1
    }
]

@app.get("/classrooms")
def get_classrooms():
    return classrooms

@app.get("/students")
def get_students():
    return students

@app.post(
    "/students",
    status_code=status.HTTP_201_CREATED
)
def create_student(student_data: StudentCreate):
    duplicated_student = next(
        (
            student
            for student in students
            if student["student_code"] == student_data.student_code
        ),
        None
    )
    if duplicated_student:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mã sinh viên đã tồn tại"
        )

    classroom = next(
        (
            classroom
            for classroom in classrooms
            if classroom["id"] == student_data.class_id
        ),
        None
    )
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lớp học không tồn tại trong hệ thống"
        )

    if classroom["status"] == "CLOSED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lớp học đã đóng"
        )

    current_students = [
        student
        for student in students
        if student["class_id"] == student_data.class_id
    ]
    if len(current_students) >= classroom["max_students"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lớp học đã đủ số lượng tối đa"
        )

    new_student = {
        "id": max([s["id"] for s in students], default=0) + 1,
        "student_code": student_data.student_code,
        "full_name": student_data.full_name,
        "class_id": student_data.class_id
    }

    students.append(new_student)
    return new_student