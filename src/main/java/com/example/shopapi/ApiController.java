package com.example.shopapi;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api")
public class ApiController {

    @Autowired private ClientRepository clientRepo;
    @Autowired private ProductRepository productRepo;
    @Autowired private OrderRepository orderRepo;

    // ================= CLIENTS =================
    @PostMapping("/clients")
    public Client createClient(@RequestBody Client client) {
        return clientRepo.save(client);
    }

    @GetMapping("/clients")
    public List<Client> getClients() {
        return clientRepo.findAll();
    }

    @PutMapping("/clients/{id}")
    public Client updateClient(@PathVariable UUID id, @RequestBody Client client) {
        client.setId(id);
        return clientRepo.save(client);
    }

    @DeleteMapping("/clients/{id}")
    public void deleteClient(@PathVariable UUID id) {
        clientRepo.deleteById(id);
    }

    // ================= PRODUCTS =================
    @PostMapping("/products")
    public Product createProduct(@RequestBody Product product) {
        return productRepo.save(product);
    }

    @GetMapping("/products")
    public List<Product> getProducts() {
        return productRepo.findAll();
    }

    @PutMapping("/products/{id}")
    public Product updateProduct(@PathVariable UUID id, @RequestBody Product product) {
        product.setId(id);
        return productRepo.save(product);
    }

    @DeleteMapping("/products/{id}")
    public void deleteProduct(@PathVariable UUID id) {
        productRepo.deleteById(id);
    }

    // ================= ORDERS =================
    @PostMapping("/orders")
    public Order createOrder(@RequestBody Order order) {
        return orderRepo.save(order);
    }

    @GetMapping("/orders")
    public List<Order> getOrders() {
        return orderRepo.findAll();
    }

    @DeleteMapping("/orders/{id}")
    public void deleteOrder(@PathVariable UUID id) {
        orderRepo.deleteById(id);
    }
}