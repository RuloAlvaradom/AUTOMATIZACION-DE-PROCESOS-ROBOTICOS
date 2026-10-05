from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

inventario_petsociety = [
    {"producto": "Blue Top", "stock_actual": 2, "stock_minimo": 5, "stock_maximo": 15},
    {"producto": "Men Tshirt", "stock_actual": 8, "stock_minimo": 5, "stock_maximo": 15},
    {"producto": "Sleeveless Dress", "stock_actual": 1, "stock_minimo": 4, "stock_maximo": 10},
    {"producto": "Winter Top", "stock_actual": 10, "stock_minimo": 6, "stock_maximo": 15},
    {"producto": "Stylish Dress", "stock_actual": 2, "stock_minimo": 5, "stock_maximo": 10},
    {"producto": "Madame Top For Women", "stock_actual": 3, "stock_minimo": 6, "stock_maximo": 12},
    {"producto": "Premium Polo T-Shirts", "stock_actual": 7, "stock_minimo": 4, "stock_maximo": 15},
    {"producto": "Lace Top For Women", "stock_actual": 1, "stock_minimo": 3, "stock_maximo": 8},
]

productos_a_comprar = []


def click_seguro(driver, elemento):
    # Usa JavaScript para hacer click, evitando el error cuando un
    # anuncio (iframe) se superpone visualmente encima del elemento
    driver.execute_script("arguments[0].click();", elemento)


def hay_sesion_iniciada(driver):
    try:
        driver.find_element(By.LINK_TEXT, "Logout")
        return True
    except NoSuchElementException:
        return False


def iniciar_sesion(driver):
    driver.get("https://www.automationexercise.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

    driver.find_element(By.CSS_SELECTOR, "input[data-qa='login-email']").send_keys("admincaso123@gmail.com")
    driver.find_element(By.CSS_SELECTOR, "input[data-qa='login-password']").send_keys("admin123")

    boton_login = driver.find_element(By.CSS_SELECTOR, "button[data-qa='login-button']")
    click_seguro(driver, boton_login)


try:
    driver.get("https://www.automationexercise.com/")

    if hay_sesion_iniciada(driver):
        print("Sesion ya iniciada, continuando compra normalmente")
    else:
        print("No hay sesion iniciada, iniciando sesion...")
        iniciar_sesion(driver)

    driver.get("https://www.automationexercise.com/products")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-image-wrapper")))

    productos = driver.find_elements(By.CLASS_NAME, "product-image-wrapper")

    catalogo_proveedor = []

    for producto in productos:
        nombre = " ".join(producto.find_element(By.CSS_SELECTOR, "div.productinfo p").text.split())
        boton = producto.find_element(By.CSS_SELECTOR, "a.add-to-cart")
        id_producto = boton.get_attribute("data-product-id")

        catalogo_proveedor.append((nombre, id_producto))

    print("\nCatalogo del proveedor obtenido:", len(catalogo_proveedor), "productos")

    for item in inventario_petsociety:
        nombre_producto = item["producto"]
        stock_petsociety = item["stock_actual"]
        stock_minimo = item["stock_minimo"]
        stock_maximo = item["stock_maximo"]

        if stock_petsociety >= stock_minimo:
            print(f"\n{nombre_producto}: stock suficiente")
            continue

        print(f"\n{nombre_producto}: bajo el minimo, se necesita reponer")

        id_proveedor = None
        for nombre_prov, id_prov in catalogo_proveedor:
            if nombre_prov == nombre_producto:
                id_proveedor = id_prov
                break

        if id_proveedor is None:
            print(f"  - !!! '{nombre_producto}' ya no esta disponible en el proveedor (descontinuado) !!!")
            continue

        cantidad_a_comprar = stock_maximo - stock_petsociety
        productos_a_comprar.append((nombre_producto, cantidad_a_comprar))
        print(f"  - ^^ Disponible, se comprara {cantidad_a_comprar} unidades (id {id_proveedor}) ^^")

    for nombre_producto, cantidad_a_comprar in productos_a_comprar:
        id_proveedor = None
        for nombre_prov, id_prov in catalogo_proveedor:
            if nombre_prov == nombre_producto:
                id_proveedor = id_prov
                break

        print(f"  > Entrando a producto {nombre_producto} (id {id_proveedor})...", flush=True)
        driver.get(f"https://www.automationexercise.com/product_details/{id_proveedor}")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "quantity")))
        print("  > Pagina cargada, escribiendo cantidad...", flush=True)

        campo_cantidad = driver.find_element(By.ID, "quantity")
        campo_cantidad.clear()
        campo_cantidad.send_keys(str(cantidad_a_comprar))

        print("  > Haciendo click en Add to cart...", flush=True)
        boton_cart = driver.find_element(By.CSS_SELECTOR, "button.cart")
        click_seguro(driver, boton_cart)

        print("  > Esperando modal...", flush=True)
        boton_cerrar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.close-modal"))
        )
        click_seguro(driver, boton_cerrar)

        print(f"  - {nombre_producto}: {cantidad_a_comprar} unidades agregadas al carrito", flush=True)
        time.sleep(1)

    driver.get("https://www.automationexercise.com/view_cart")
    print("\nCarrito actualizado, revisa el navegador para confirmar.")

except NoSuchElementException:
    print("Elemento no encontrado")
except Exception as e:
    print("Error:", e)
finally:
    time.sleep(8)
    driver.quit()