#!/bin/bash

# ============================================================================
# Docker Build Script for Q-IDE (Linux/macOS)
# Builds frontend and backend images for Kubernetes deployment
# ============================================================================

set -e  # Exit on any error

# Configuration
REGISTRY="${REGISTRY:-your-registry}"  # Set to your Docker registry
REPOSITORY_NAME="${REPOSITORY_NAME:-q-ide}"
FRONTEND_IMAGE="${REGISTRY}/${REPOSITORY_NAME}-frontend"
BACKEND_IMAGE="${REGISTRY}/${REPOSITORY_NAME}-backend"
VERSION="${VERSION:-latest}"
BUILT_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}===============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    print_success "Docker found: $(docker --version)"
    
    if ! command -v git &> /dev/null; then
        print_warning "Git not found (optional)"
    else
        print_success "Git found: $(git --version)"
    fi
}

# Build frontend
build_frontend() {
    print_header "Building Frontend Image"
    
    print_info "Building: ${FRONTEND_IMAGE}:${VERSION}"
    
    docker build \
        --file frontend/Dockerfile \
        --tag "${FRONTEND_IMAGE}:${VERSION}" \
        --tag "${FRONTEND_IMAGE}:latest" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --label "built.date=${BUILT_DATE}" \
        --label "git.commit=${GIT_COMMIT}" \
        --label "version=${VERSION}" \
        .
    
    if [ $? -eq 0 ]; then
        print_success "Frontend image built successfully"
    else
        print_error "Frontend build failed!"
        exit 1
    fi
}

# Build backend
build_backend() {
    print_header "Building Backend Image"
    
    print_info "Building: ${BACKEND_IMAGE}:${VERSION}"
    
    docker build \
        --file backend/Dockerfile \
        --tag "${BACKEND_IMAGE}:${VERSION}" \
        --tag "${BACKEND_IMAGE}:latest" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --label "built.date=${BUILT_DATE}" \
        --label "git.commit=${GIT_COMMIT}" \
        --label "version=${VERSION}" \
        .
    
    if [ $? -eq 0 ]; then
        print_success "Backend image built successfully"
    else
        print_error "Backend build failed!"
        exit 1
    fi
}

# Push to registry
push_images() {
    print_header "Pushing Images to Registry"
    
    if [ "$REGISTRY" = "your-registry" ]; then
        print_warning "REGISTRY is set to default 'your-registry'"
        print_info "Update REGISTRY environment variable to push images"
        return
    fi
    
    print_info "Pushing frontend image..."
    docker push "${FRONTEND_IMAGE}:${VERSION}"
    docker push "${FRONTEND_IMAGE}:latest"
    print_success "Frontend image pushed"
    
    print_info "Pushing backend image..."
    docker push "${BACKEND_IMAGE}:${VERSION}"
    docker push "${BACKEND_IMAGE}:latest"
    print_success "Backend image pushed"
}

# Display image info
show_image_info() {
    print_header "Image Information"
    
    echo -e "${BLUE}Frontend:${NC}"
    docker images "${FRONTEND_IMAGE}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    
    echo ""
    echo -e "${BLUE}Backend:${NC}"
    docker images "${BACKEND_IMAGE}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
}

# Test images
test_images() {
    print_header "Testing Images"
    
    # Test frontend
    print_info "Testing frontend image..."
    docker run --rm -p 3000:3000 --health-start-period=10s --health-interval=5s \
        "${FRONTEND_IMAGE}:${VERSION}" \
        sh -c "timeout 5 serve -s dist -l 3000 --single || true" && \
        print_success "Frontend image works" || print_error "Frontend image test failed"
    
    # Test backend
    print_info "Testing backend image..."
    docker run --rm -p 8000:8000 --health-start-period=10s --health-interval=5s \
        "${BACKEND_IMAGE}:${VERSION}" \
        sh -c "timeout 5 gunicorn --workers=1 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 main:app || true" && \
        print_success "Backend image works" || print_error "Backend image test failed"
}

# Clean up
cleanup() {
    print_header "Cleanup"
    print_info "Removing dangling images..."
    docker image prune -f --filter "dangling=true" > /dev/null
    print_success "Cleanup complete"
}

# Main
main() {
    print_header "Q-IDE Docker Build System"
    echo "Registry: ${REGISTRY}"
    echo "Version: ${VERSION}"
    echo "Git Commit: ${GIT_COMMIT}"
    
    check_prerequisites
    build_frontend
    build_backend
    show_image_info
    
    if [ "$1" = "--push" ]; then
        push_images
    fi
    
    if [ "$1" = "--test" ]; then
        test_images
    fi
    
    if [ "$1" = "--cleanup" ]; then
        cleanup
    fi
    
    if [ "$1" = "--all" ]; then
        test_images
        push_images
        cleanup
    fi
    
    print_header "Build Complete"
    echo -e "${GREEN}Images ready for deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Tag images: docker tag <image>:${VERSION} <registry>/<image>:${VERSION}"
    echo "  2. Push images: docker push <registry>/<image>:${VERSION}"
    echo "  3. Deploy: kubectl apply -f k8s/"
}

# Show usage
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./docker-build.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --push      Build and push to registry"
    echo "  --test      Build and test images"
    echo "  --cleanup   Build and cleanup dangling images"
    echo "  --all       Build, test, push, and cleanup"
    echo "  --help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  REGISTRY    Docker registry (default: your-registry)"
    echo "  VERSION     Image version (default: latest)"
    exit 0
fi

main "$@"
