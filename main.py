"""  
Lỗi 1: Lỗi đồng bộ ngược (Lỗi ở quan hệ 1 - N) 
    - Lỗi: students = relationship("Student", back_populates="department_id")
    - Nguyên nhân: back_populates yêu cầu phải trỏ đến tên thuộc tính quan hệ (relationship) ở class đối diện, chứ không phải tên cột khóa ngoại (Column).
    -> Sửa: students = relationship("Student", back_populates="department")

Lỗi 2: Lỗi cấu hình collection (Lỗi ở quan hệ 1 - 1) 
    - Lỗi: profile = relationship("Profile", back_populates="student")
    - Nguyên nhân: Mặc định, hàm relationship() trong SQLAlchemy sẽ coi mọi liên kết là quan hệ 1-N (trả về một danh sách/list các đối tượng).
    -> Sửa: profile = relationship("Profile", back_populates="student", uselist=False)

Lỗi 3: Thiếu cấu hình bảng trung gian secondary (Lỗi ở quan hệ N - N) 
    - Lỗi:
        courses = relationship("Course", back_populates="students") # Ở class Student
        students = relationship("Student", back_populates="courses") # Ở class Course

    - Nguyên nhân: Quan hệ Nhiều - Nhiều, SQLAlchemy không thể tự động biết dữ liệu liên kết được lưu ở đâu nếu không có bảng trung gian.
    -> Sửa: 
        courses = relationship("Course", secondary=student_course, back_populates="students")

        students = relationship("Student", secondary=student_course, back_populates="courses")

"""





from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base # Giả định Base 

student_course = Table(
    "student_course", 
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    students = relationship("Student", back_populates="department")


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="students")
    
    profile = relationship("Profile", back_populates="student", uselist=False)
    
    courses = relationship("Course", secondary= student_course, back_populates="students")

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    bio = Column(String(255))

    student_id = Column(Integer, ForeignKey("students.id"))
    student = relationship("Student", back_populates="profile")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)

    students = relationship("Student", secondary= student_course, back_populates="courses")