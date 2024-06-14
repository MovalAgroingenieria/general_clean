<html>
    <head>
        <meta charset="UTF-8">
        <title>Electronic Office</title>
    </head>
    <body>
        <?php
        // Certificate OK?
        $dir = "/tmp/";
        $RootCA = "/etc/ssl/certs/ac_raiz_dnie_2_ac_raiz_fnmt_rcm.crt";
        $OCSPUrl = "http://ocsp.dnie.es/";
        if ($_SERVER["SSL_CLIENT_I_DN_O"] == "FNMT-RCM") {
            $OCSPUrl = "http://ocspusu.cert.fnmt.es/ocspusu/OcspResponder/";
        }
        $a = rand(1000,99999);
        $content_issuer_cert = $_SERVER["SSL_CLIENT_CERT_CHAIN_0"]; // Intermediate certificate (in the browser).
        $content_client_cert = $_SERVER["SSL_CLIENT_CERT"]; // User certificate (chip or installed).
        $content_issuer_cert = str_replace("-----BEGIN CERTIFICATE-----", "", $content_issuer_cert);
        $content_issuer_cert = str_replace("-----END CERTIFICATE-----", "", $content_issuer_cert);
        $content_issuer_cert = preg_replace("/\r|\n/", "", $content_issuer_cert);
        $content_issuer_cert = "-----BEGIN CERTIFICATE-----\n".$content_issuer_cert."\n-----END CERTIFICATE-----";
        $content_client_cert = str_replace("-----BEGIN CERTIFICATE-----", "", $content_client_cert);
        $content_client_cert = str_replace("-----END CERTIFICATE-----", "", $content_client_cert);
        $content_client_cert = preg_replace("/\r|\n/", "", $content_client_cert);
        $content_client_cert = "-----BEGIN CERTIFICATE-----\n".$content_client_cert."\n-----END CERTIFICATE-----";
        file_put_contents($dir.$a."cert_i.pem", $content_issuer_cert);
        file_put_contents($dir.$a."cert_c.pem", $content_client_cert);
        $output = shell_exec("openssl ocsp -CAfile ".$RootCA." -issuer ".$dir.$a."cert_i.pem -cert ".$dir.$a."cert_c.pem -url ".$OCSPUrl);
        $output = preg_split("/[\r\n]/", $output);
        $output = preg_split("/: /", $output[0]);
        $ocsp = $output[1];
        // Get data from the digital certificate.
        if ($ocsp == "good") {
            $complete_identification = $_SERVER["SSL_CLIENT_S_DN"];
            $country = $_SERVER["SSL_CLIENT_S_DN_C"];
            $first_name = $_SERVER["SSL_CLIENT_S_DN_G"];
            $last_name = $_SERVER["SSL_CLIENT_S_DN_S"];
            $authority = $_SERVER["SSL_CLIENT_I_DN_O"];
            $parts = explode('serialNumber=', $complete_identification);
            $raw_dni = $parts[1];
            $parts = explode(',', $raw_dni);
            $dni = $parts[0];
            $parts = explode('-', $dni);
            if (count($parts) == 2) {
                $dni = $parts[1];
            }
            $data_to_encrypt = $country.":".$dni.":".$last_name.":".$first_name.":".$authority.":";
            // Provisional
            /* echo "country:<br/>";
            echo $country;
            echo "<br/><br/>dni:<br/>";
            echo $dni;
            echo "<br/><br/>first_name:<br/>";
            echo $first_name;
            echo "<br/><br/>last_name:<br/>";
            echo $last_name;
            echo "<br/><br/>authority:<br/>";
            echo $authority;
            echo "<br/><br/>data_to_encrypt:<br/>";
            echo $data_to_encrypt; */
            // Values for redirection to Odoo: "cipher_key" (private) and "frontend_url".
            // IMPORTANT: Update the frontend_url (Odoo instance) and cipher_key variables.
            $frontend_url = 'http://127.0.0.1:9166/eoffice';
            $cipher_key = 'a%C*F-JaNdRgUkXqj8Ymx59IYhv0vHe2';
            // Encrypt.
            $method = "AES-128-CBC";
            if (strlen($cipher_key) == 24) {
                $method = "AES-192-CBC";
            } else {
                if (strlen($cipher_key) == 32) {
                    $method = "AES-256-CBC";
                }    
            }
            $iv = openssl_random_pseudo_bytes(openssl_cipher_iv_length($method));
            $encrypted_raw = openssl_encrypt($data_to_encrypt, $method, $cipher_key, $options=OPENSSL_RAW_DATA, $iv);
            $identif_token = base64_encode($iv.$encrypted_raw);
            $_SERVER["FRONTEND_URL"] = $frontend_url;
            $_SERVER["IDENTIF_TOKEN"] = $identif_token;
            // Provisional
            /* echo "<br/><br/>identif_token:<br/>";
            echo $identif_token; */
        } else {
            echo "OCSP: revoked or unknown";
        }
        ?>

        <!-- Automatic redirection to Odoo-frontend. -->        
        <form id="hidden_form" method="post" action="<?php echo $_SERVER["FRONTEND_URL"]?>">
            <input type="hidden" name="identif_token" value="<?php echo $_SERVER["IDENTIF_TOKEN"]?>">
            <input type="submit" id="hidden_button" style="display:block;" value="Click">
        </form>
        <script>
            document.getElementById("hidden_button").style.display="none";
            document.getElementById("hidden_form").submit();
        </script>
        
    </body>
</html>
