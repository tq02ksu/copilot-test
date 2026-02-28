package com.example.usermanagement.service;

import com.example.usermanagement.entity.User;
import com.example.usermanagement.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class UserService {

    private final UserRepository userRepository;

    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User createUser(User user) {
        if (userRepository.existsByUsername(user.getUsername())) {
            throw new IllegalArgumentException("用户名已存在: " + user.getUsername());
        }
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new IllegalArgumentException("邮箱已存在: " + user.getEmail());
        }
        return userRepository.save(user);
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    public Optional<User> getUserById(Long id) {
        return userRepository.findById(id);
    }

    public User updateUser(Long id, User userDetails) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在，ID: " + id));

        if (!user.getUsername().equals(userDetails.getUsername()) 
                && userRepository.existsByUsername(userDetails.getUsername())) {
            throw new IllegalArgumentException("用户名已存在: " + userDetails.getUsername());
        }

        if (!user.getEmail().equals(userDetails.getEmail()) 
                && userRepository.existsByEmail(userDetails.getEmail())) {
            throw new IllegalArgumentException("邮箱已存在: " + userDetails.getEmail());
        }

        user.setUsername(userDetails.getUsername());
        user.setEmail(userDetails.getEmail());
        return userRepository.save(user);
    }

    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new IllegalArgumentException("用户不存在，ID: " + id);
        }
        userRepository.deleteById(id);
    }
}
