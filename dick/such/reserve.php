<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'vendor/autoload.php'; // Потрібен Composer для PHPMailer

error_reporting(E_ALL);
ini_set('display_errors', 1);

$host = 'localhost';
$dbname = 'restoran';
$username = 'root';
$password = '';

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

$conn = new mysqli($host, $username, $password, $dbname);
if ($conn->connect_error) {
    die("Помилка підключення: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (!isset($_POST['name'], $_POST['email'], $_POST['date'], $_POST['time'])) {
        die("Помилка: усі поля повинні бути заповнені.");
    }

    $name = $conn->real_escape_string($_POST['name']);
    $email = $conn->real_escape_string($_POST['email']);
    $date = $conn->real_escape_string($_POST['date']);
    $time = $conn->real_escape_string($_POST['time']);
    
    $stmt = $conn->prepare("INSERT INTO reservations (name, email, date, time) VALUES (?, ?, ?, ?)");
    if (!$stmt) {
        die("Помилка підготовки запиту: " . $conn->error);
    }
    
    $stmt->bind_param("ssss", $name, $email, $date, $time);
    if (!$stmt->execute()) {
        die("Помилка виконання запиту: " . $stmt->error);
    }
    
    $stmt->close();
    
    $mail = new PHPMailer(true);
    try {
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com';
        $mail->SMTPAuth = true;
        $mail->Username = 'kostiuk773@gmail.com'; // Заміни на свій email
        $mail->Password = 'xgcngzocwtcpcryo'; // Використовуй App Password від Gmail
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port = 587;

        $mail->setFrom('kostiuk773@gmail.com', 'Delicious');
        $mail->addAddress($email);
        $mail->isHTML(true);
        $mail->Subject = "Підтвердження бронювання";
        $mail->Body = "<html><body>Ви забронювали столик у ресторані на $date о $time. Дякуємо!</body></html>";

        $mail->send();
        echo "<script>alert('Ваше бронювання підтверджено! Перевірте email.'); window.location.href='index.html';</script>";
    } catch (Exception $e) {
        die("Помилка надсилання email: " . $mail->ErrorInfo);
    }
}
$conn->close();
?>