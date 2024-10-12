import React from "react";
import { useForm } from "react-hook-form";
import { AuthActions } from "@/app/auth/utils";
import { useRouter } from "next/navigation";

type FormData = {
  email: string;
  username: string;
  password: string;
};

const Register = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<FormData>();

  const router = useRouter();
  const { register: registerUser } = AuthActions(); // Note: Renamed to avoid naming conflict with useForm's register

  const onSubmit = (data: FormData) => {
    registerUser(data.email, data.username, data.password)
      .json(() => {
        router.push("/"); // Adjust the path as needed
      })
      .catch((err) => {
        console.error("Registration error:", err); // Log the error

        let errorMessage = "Registration failed. Please try again.";
        if (err.status === 400) {
          errorMessage = err.json.detail || errorMessage; // Assuming 400 status returns detailed message
        } else if (err.status === 500) {
          errorMessage = "Internal server error. Please try again later.";
        }

        setError("root", {
          type: "manual",
          message: errorMessage,
        });
      });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="px-8 py-6 mt-4 text-left bg-white shadow-lg w-1/3">
        <h3 className="text-2xl font-semibold">Register your account</h3>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-4">
          <div>
            <label className="block" htmlFor="email">
              Email
            </label>
            <input
              type="text"
              placeholder="Email"
              {...register("email", { required: "Email is required" })}
              className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
            {errors.email && (
              <span className="text-xs text-red-600">
                {errors.email.message}
              </span>
            )}
          </div>
          <div className="mt-4">
            <label className="block" htmlFor="username">
              Username
            </label>
            <input
              type="text"
              placeholder="Username"
              {...register("username", { required: "Username is required" })}
              className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
            {errors.username && (
              <span className="text-xs text-red-600">
                {errors.username.message}
              </span>
            )}
          </div>
          <div className="mt-4">
            <label className="block" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              placeholder="Password"
              {...register("password", { required: "Password is required" })}
              className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
            {errors.password && (
              <span className="text-xs text-red-600">
                {errors.password.message}
              </span>
            )}
          </div>
          <div className="flex items-center justify-between mt-4">
            <button
              type="submit"
              className="px-12 py-2 leading-5 text-white transition-colors duration-200 transform bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:bg-blue-700"
            >
              Register
            </button>
          </div>
          {errors.root && (
            <span className="text-xs text-red-600">{errors.root.message}</span>
          )}
        </form>
      </div>
    </div>
  );
};

export default Register;
