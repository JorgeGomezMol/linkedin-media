<?php
// Simple contact handler for sereniumfinance.com/contact/
$to = 'hello@sereniumfinance.com';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contact/'); exit; }
if (!empty($_POST['website'])) { header('Location: /contact/?sent=1'); exit; } // honeypot
function clean($v, $max) { $v = trim(strip_tags((string)$v)); $v = str_replace(["\r", "\n"], ' ', $v); return mb_substr($v, 0, $max); }
$name    = clean($_POST['name'] ?? '', 120);
$email   = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
$company = clean($_POST['company'] ?? '', 200);
$topic   = clean($_POST['topic'] ?? '', 40);
$message = mb_substr(trim(strip_tags((string)($_POST['message'] ?? ''))), 0, 3000);
if ($name === '' || !$email) { header('Location: /contact/?sent=0'); exit; }
$body = "Name: $name\nEmail: $email\nCompany: $company\nInterested in: $topic\n\n$message\n";
$headers = "From: Serenium website <$to>\r\nReply-To: $email\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$ok = mail($to, "Website inquiry: $name", $body, $headers);
header('Location: /contact/?sent=' . ($ok ? '1' : '0'));
exit;
