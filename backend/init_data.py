import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
import django
django.setup()

from api.models import Category, Book, User


def init_data():
    print("开始创建测试数据...\n")

    categories = [
        {'name': '文学小说', 'description': '各类文学作品和小说'},
        {'name': '科技计算机', 'description': '计算机科学与技术书籍'},
        {'name': '历史传记', 'description': '历史著作和人物传记'},
        {'name': '经济管理', 'description': '经济学和管理学书籍'},
        {'name': '艺术设计', 'description': '艺术和设计相关书籍'},
    ]

    for cat in categories:
        if not Category.objects.filter(name=cat['name']).exists():
            Category.objects.create(**cat)
            print(f'创建分类: {cat["name"]}')

    print()

    lit_cat = Category.objects.get(name='文学小说')
    tech_cat = Category.objects.get(name='科技计算机')
    hist_cat = Category.objects.get(name='历史传记')

    books = [
        {
            'isbn': '9787020002207',
            'title': '红楼梦',
            'author': '曹雪芹',
            'publisher': '人民文学出版社',
            'publish_date': '2008-07-01',
            'category': lit_cat,
            'description': '《红楼梦》是中国古典四大名著之首，以贾宝玉、林黛玉、薛宝钗的爱情婚姻悲剧为主线。',
            'location': 'A区-01架-03层',
            'total_quantity': 5,
            'available_quantity': 5,
            'status': 'available'
        },
        {
            'isbn': '9787111213826',
            'title': 'Python编程从入门到实践',
            'author': 'Eric Matthes',
            'publisher': '机械工业出版社',
            'publish_date': '2016-07-01',
            'category': tech_cat,
            'description': '一本针对所有层次的Python读者而作的Python入门书。',
            'location': 'B区-02架-01层',
            'total_quantity': 3,
            'available_quantity': 3,
            'status': 'available'
        },
        {
            'isbn': '9787108044624',
            'title': '明朝那些事儿',
            'author': '当年明月',
            'publisher': '浙江人民出版社',
            'publish_date': '2017-05-01',
            'category': hist_cat,
            'description': '主要讲述的是从1344年到1644年这三百年间关于明朝的一些事情。',
            'location': 'C区-01架-02层',
            'total_quantity': 4,
            'available_quantity': 4,
            'status': 'available'
        },
        {
            'isbn': '9787020002214',
            'title': '三国演义',
            'author': '罗贯中',
            'publisher': '人民文学出版社',
            'publish_date': '2010-01-01',
            'category': lit_cat,
            'description': '《三国演义》描写了从东汉末年到西晋初年之间近百年的历史风云。',
            'location': 'A区-01架-01层',
            'total_quantity': 5,
            'available_quantity': 5,
            'status': 'available'
        },
        {
            'isbn': '9787115428028',
            'title': '深入理解计算机系统',
            'author': 'Randal E. Bryant',
            'publisher': '机械工业出版社',
            'publish_date': '2016-11-01',
            'category': tech_cat,
            'description': '本书从程序员的视角详细阐述计算机系统的本质概念。',
            'location': 'B区-03架-05层',
            'total_quantity': 2,
            'available_quantity': 2,
            'status': 'available'
        },
        {
            'isbn': '9787544270878',
            'title': '活着',
            'author': '余华',
            'publisher': '作家出版社',
            'publish_date': '2012-08-01',
            'category': lit_cat,
            'description': '讲述了农村人福贵悲惨的人生遭遇。',
            'location': 'A区-02架-03层',
            'total_quantity': 6,
            'available_quantity': 6,
            'status': 'available'
        },
    ]

    for book_data in books:
        if not Book.objects.filter(isbn=book_data['isbn']).exists():
            Book.objects.create(**book_data)
            print(f'创建图书: {book_data["title"]}')

    print()

    readers = [
        {'username': 'reader1', 'email': 'reader1@test.com', 'first_name': '张', 'last_name': '三', 'role': 'reader', 'phone': '13800138001'},
        {'username': 'reader2', 'email': 'reader2@test.com', 'first_name': '李', 'last_name': '四', 'role': 'reader', 'phone': '13800138002'},
    ]

    for reader_data in readers:
        if not User.objects.filter(username=reader_data['username']).exists():
            user = User.objects.create_user(**reader_data, password='123456')
            print(f'创建读者: {reader_data["username"]} / 123456')

    print("\n测试数据创建完成！")
    print("\n=== 账号信息 ===")
    print("管理员: admin / admin123")
    print("读者1: reader1 / 123456")
    print("读者2: reader2 / 123456")
    print("\n=== 访问地址 ===")
    print("前端: http://localhost:5110")
    print("后端API: http://localhost:3100")


if __name__ == '__main__':
    init_data()
