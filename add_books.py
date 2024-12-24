import sqlite3

DB_NAME = 'data/data.db'

def insert_books():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    books = [
        ('In Too Deep', 199, 'img1.jpg'),
        ('Into the Water', 149, 'img2.jpg'),
        ('The Silent Love', 399, 'img3.jpg'),
        ('It Ends With Us', 599, 'img4.jpg'),
        ('Never Lie', 249, 'img5.jpg'),
        ('An Eye for an Eye', 499, 'img6.jpg'),
        ('The Devils', 899, 'img7.jpg'),
        ('The Women in the Window', 649, 'img8.jpg'),
        ('Pretty Girls', 599, 'img9.jpg'),
        ('Rich Dad Poor Dad', 179, 'img10.jpg'),
        ('Harry Potter', 579, 'img11.jpg'),
        ('Atomic Habits', 249, 'img12.jpg')
    ]

    cursor.executemany("INSERT INTO books (name, price, image) VALUES (?, ?, ?)", books)

    conn.commit()
    conn.close()

    print("Books inserted successfully!")

if __name__ == '__main__':
    insert_books()
